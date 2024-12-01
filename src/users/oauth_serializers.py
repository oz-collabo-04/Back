import re
from datetime import datetime, timezone

from django.contrib.sites import requests
from rest_framework import serializers
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from common.exceptions import BadRequestException, UnauthorizedException
from common.logging_config import logger
from users.models import User


class AllowExpiredTokenPermission(BasePermission):
    """
    특정 API 경로에서 만료된 토큰을 허용하는 권한 클래스.
    - /api/v1/users/token/refresh/ 경로에서는 만료된 토큰도 검증을 허용함.
    """

    def has_permission(self, request, view):
        # 특정 경로에서는 만료된 토큰 허용
        if request.path == "/api/v1/users/token/refresh/":
            return True
        # 그 외에는 기본 인증된 사용자만 접근 가능
        return request.user and request.user.is_authenticated

# 토큰 재발급시 액세스토큰이 만료 되있어도 그이후 로직이 수행되도록 인증을 풀어줌
class CustomAuthenticationToken(JWTAuthentication):
    """
    특정 API 경로에서 만료된 액세스 토큰을 허용하는 커스텀 인증 클래스.
    - /api/v1/users/token/refresh/ 경로에서는 만료된 토큰도 디코딩할 수 있도록 처리.
    """

    def authenticate(self, request):
        header = self.get_header(request)  # Authorization 헤더 가져오기
        raw_token = self.get_raw_token(header)  # 토큰 값 추출

        # 특정 경로에서는 Authorization 헤더가 없어도 동작 가능하도록 설정
        if request.path == "/api/v1/users/token/refresh/":
            if not header or not raw_token:
                return None

        # Authorization 헤더가 없을 경우 예외 처리
        if not header:
            raise UnauthorizedException(
                detail="Authorization 헤더가 누락되었습니다.", code="MISSING_AUTHORIZATION_HEADER"
            )

        # 유효한 토큰 값이 없을 경우 예외 처리
        if not raw_token:
            raise UnauthorizedException(
                detail="Authorization 헤더에 유효한 토큰이 포함되어 있지 않습니다.", code="INVALID_AUTHORIZATION_HEADER"
            )

        try:
            # 기본 토큰 유효성 검증
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except InvalidToken as e:
            # 만료된 토큰 처리 (특정 경로에 한함)
            if request.path == "/api/v1/users/token/refresh/":
                try:
                    # 만료 여부 무시하고 토큰 디코딩
                    token = AccessToken(raw_token, verify=False)
                    return None, token
                except InvalidToken:
                    raise UnauthorizedException(
                        detail="유효하지 않은 액세스 토큰입니다.", code="INVALID_ACCESS_TOKEN"
                    ) from e
            else:
                raise UnauthorizedException(detail="유효하지 않은 액세스 토큰입니다.", code="INVALID_ACCESS_TOKEN")


class AccessTokenSerializer(serializers.Serializer):
    """
    Access Token 생성 Serializer.
    """

    def create_access_token(self, user):
        """
        새로운 Access Token을 생성.
        """
        if not user:
            raise BadRequestException("유효하지 않은 사용자입니다.", code="INVALID_USER")

        # 새 Access Token 생성
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class RefreshTokenSerializer(serializers.Serializer):
    """
    리프레시 토큰 직렬화기
    - 리프레시 토큰의 유효성을 검증하고 새로운 토큰을 발급.
    """

    refresh_token = serializers.CharField(max_length=512, write_only=True, help_text="발급된 리프레시 토큰")

    def validate_refresh_token(self, value):
        """
        리프레시 토큰 유효성 검증
        """
        if not value:
            raise BadRequestException("리프레시 토큰이 필요합니다.", code="MISSING_REFRESH_TOKEN")

        if len(value) > 512:
            raise BadRequestException("리프레시 토큰의 길이가 너무 깁니다.", code="REFRESH_TOKEN_TOO_LONG")

        try:
            token = RefreshToken(value)
        except Exception as e:
            raise BadRequestException("유효하지 않은 리프레시 토큰입니다.", code="INVALID_REFRESH_TOKEN") from e

        exp_timestamp = token["exp"]
        current_time = datetime.now(tz=timezone.utc).timestamp()
        if current_time >= exp_timestamp:
            raise BadRequestException("리프레시 토큰이 만료되었습니다.", code="REFRESH_TOKEN_EXPIRED")

        return value

    def create_refresh_token(self, user):
        """
        기존 리프레시 토큰을 제거하고 새로운 리프레시 토큰 생성.
        """
        self._blacklist_existing_refresh_tokens(user)
        refresh = RefreshToken.for_user(user)
        return str(refresh)

    def _blacklist_existing_refresh_tokens(self, user):
        """
        사용자의 기존 리프레시 토큰을 블랙리스트에 추가.
        """
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception as e:
                logger.error(f"리프레시 토큰 블랙리스트 처리 중 오류 발생: {str(e)}")
        outstanding_tokens.delete()

class SocialLoginSerializer(serializers.Serializer):
    """소셜 로그인 공통 시리얼라이저"""

    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    email = serializers.EmailField(required=True)
    profile_image = serializers.URLField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        if not value:
            raise BadRequestException("사용자 이메일이 제공되지 않았습니다.", code="missing_email")
        return value

    def validate_phone_number(self, value):
        """
        전화번호 유효성 검증 및 표준화
        - 전화번호는 항상 010-0000-0000 형태로 변환.
        """
        if not value:
            return None

        phone_number = re.sub(r"[^\d]", "", value)
        if phone_number.startswith("82"):
            phone_number = "0" + phone_number[2:]

        if len(phone_number) not in (10, 11):
            raise BadRequestException("전화번호 형식이 올바르지 않습니다.", code="invalid_phone_number")

        if len(phone_number) == 10:
            formatted_phone_number = f"{phone_number[:3]}-{phone_number[3:6]}-{phone_number[6:]}"
        else:
            formatted_phone_number = f"{phone_number[:3]}-{phone_number[3:7]}-{phone_number[7:]}"

        return phone_number

    def save(self, **kwargs):
        """
        사용자 생성 또는 업데이트
        - 이메일을 기준으로 사용자 정보를 저장하거나 기존 사용자 업데이트.
        """
        validated_data = {**self.validated_data, **kwargs}
        email = validated_data["email"]
        name = validated_data.get("name", "")
        profile_image = self._clean_profile_image(validated_data.get("profile_image", ""))
        phone_number = validated_data.get("phone_number", "")

        # 이메일을 기준으로 사용자 검색
        user = User.objects.filter(email=email).first()

        if user:
            # 기존 사용자 업데이트
            user.name = name or user.name
            user.profile_image = profile_image or user.profile_image
            user.phone_number = phone_number or user.phone_number
            user.is_active = True  # 활성화 상태 설정
        else:
            # 새로운 사용자 생성
            user = User(email=email, name=name, profile_image=profile_image, phone_number=phone_number)

        user.save()

        # 기존 리프레시 토큰 블랙리스트 처리
        self._blacklist_existing_refresh_tokens(user)

        return user

    def _clean_profile_image(self, profile_image_url):
        """
        소셜 로그인 프로필 이미지 URL을 정리하여 저장.
        """
        if profile_image_url and profile_image_url.startswith("/media/"):
            # Remove "/media/" and decode the URL-encoded characters
            clean_url = profile_image_url[len("/media/"):]
            return requests.utils.unquote(clean_url)
        return profile_image_url

    def _blacklist_existing_refresh_tokens(self, user):
        """
        유저의 기존 리프레시 토큰을 블랙리스트 처리.
        """
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception as e:
                logger.error(f"토큰 블랙리스트 처리 중 오류 발생: {str(e)}")
        outstanding_tokens.delete()
