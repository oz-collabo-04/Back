import re
from datetime import datetime, timezone

from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

from common.exceptions import BadRequestException
from common.logging_config import logger
from users.models import User


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


class SocialLoginSerializer(serializers.ModelSerializer):
    """
    소셜 로그인 공통 시리얼라이저
    """

    gender = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "email", "name", "gender", "phone_number", "profile_image", "is_expert"]
        read_only_fields = [
            "id",
            "is_expert",
        ]
        extra_kwargs = {
            "email": {
                "required": True,
                "validators": [],  # 고유성 검증 제거
            },
            "name": {"required": True},
        }

    def validate_email(self, value):
        # 이메일 유효성은 확인하되, 고유성 검증은 우회
        if not value:
            raise serializers.ValidationError("이메일은 필수 항목입니다.")
        return value.strip().lower()

    def validate_gender(self, value):
        gender = value.strip().upper()
        if gender in ["MALE", "M"]:
            return "M"
        elif gender in ["FEMALE", "F"]:
            return "F"
        else:
            return "F"  # 기본값

    def validate_phone_number(self, value):
        phone_number = re.sub(r"[^\d]", "", value)  # 숫자만 남기기
        if phone_number.startswith("82"):  # 국제번호 제거
            phone_number = "0" + phone_number[2:]

        # 전화번호 형식 변환
        if len(phone_number) == 11:  # 11자리 번호
            formatted_phone = f"{phone_number[:3]}-{phone_number[3:7]}-{phone_number[7:]}"
        elif len(phone_number) == 10:  # 10자리 번호
            formatted_phone = f"{phone_number[:3]}-{phone_number[3:6]}-{phone_number[6:]}"
        else:
            raise serializers.ValidationError("유효한 전화번호 형식이 아닙니다.")

        # 전화번호 길이 검증
        if len(formatted_phone) > 13:
            raise serializers.ValidationError("전화번호는 13자를 초과할 수 없습니다.")

        return formatted_phone

    def create(self, validated_data):
        try:
            with transaction.atomic():
                # 이메일을 기반으로 사용자 검색 또는 생성
                user, created = User.objects.update_or_create(
                    email=validated_data["email"],
                    defaults=validated_data,
                )

                # 프로필 이미지 처리
                profile_image = validated_data.get("profile_image")
                if profile_image:
                    user.profile_image.save(profile_image.name, profile_image)
                    user.save()

                return user
        except IntegrityError:
            raise serializers.ValidationError("이미 동일한 이메일이 존재합니다.")

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
