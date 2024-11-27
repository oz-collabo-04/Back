import requests
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from common.exceptions import CustomAPIException
from users.models import User
from users.seriailzers import UserInfoSerializer


# #### 소셜 로그인 / 네이버, 카카오, 구글/
class NaverLoginCallbackAPIView(APIView):
    @extend_schema(
        tags=["Oauth"],
        summary="네이버 서버인증, 액세스, 리프레시 토큰발급, 유저생성",
        parameters=[
            OpenApiParameter(
                "code", OpenApiTypes.STR, OpenApiParameter.QUERY, description="네이버 인증 후 반환된 코드"
            ),
            OpenApiParameter(
                "state", OpenApiTypes.STR, OpenApiParameter.QUERY, description="CSRF 공격 방지를 위한 상태 값"
            ),
        ],
        responses={
            200: {"type": "object", "description": "로그인 성공"},
            400: {"type": "object", "description": "잘못된 요청"},
            403: {"type": "object", "description": "네이버 API 호출 실패"},
        },
    )
    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        state = request.data.get("state")

        if not code or not state:
            raise CustomAPIException("code 또는 state 값이 누락되었습니다.", code="missing_parameters")

        # 네이버 액세스 토큰 요청
        access_token_data = self.get_naver_access_token(code, state)
        access_token = access_token_data.get("access_token")
        if not access_token:
            raise CustomAPIException("네이버에서 액세스 토큰을 가져오지 못했습니다.", code="token_fetch_failed")

        # 사용자 정보 요청
        user_info = self.get_naver_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(AccessToken.for_user(user))
        user_data = UserInfoSerializer(user).data

        # 응답 생성
        response = Response({"access_token": access_token, "user": user_data}, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", str(refresh), httponly=True, secure=True, samesite="Lax")
        return response

    def get_naver_access_token(self, code, state):
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "code": code,
            "state": state,
        }
        response = requests.post(settings.NAVER_TOKEN_URL, params=payload)
        if response.status_code != 200 or "error" in response.json():
            raise CustomAPIException("네이버에서 액세스 토큰을 가져오는 데 실패했습니다.", code="token_fetch_failed")
        return response.json()

    def get_naver_user_info(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(settings.NAVER_USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            raise CustomAPIException(
                "네이버에서 사용자 정보를 가져오는 데 실패했습니다.", code="user_info_fetch_failed"
            )
        return response.json()

    def create_or_update_user(self, user_info):
        response_data = user_info.get("response", {})
        name = response_data.get("name", "네이버 사용자")
        email = response_data.get("email")
        profile_image = response_data.get("profile_image")
        phone_number = response_data.get("mobile")

        user = User.objects.filter(email=email).first() or User.objects.filter(phone_number=phone_number).first()
        if user:
            user.name = name or user.name
            user.profile_image = profile_image or user.profile_image
            if phone_number:
                user.phone_number = phone_number
        else:
            user = User(email=email, name=name, profile_image=profile_image, phone_number=phone_number)

        user.save()
        return user


class KakaoLoginCallbackAPIView(APIView):
    @extend_schema(
        tags=["Oauth"],
        summary="카카오 서버인증, 액세스, 리프레시 토큰발급, 유저생성",
        request={
            "type": "object",
            "properties": {
                "code": {"type": "string", "example": "AQAAAAAA1234", "description": "카카오 인증 후 반환된 코드"}
            },
            "required": ["code"],
        },
        responses={
            200: {"type": "object", "description": "로그인 성공"},
            400: {"type": "object", "description": "잘못된 요청"},
            403: {"type": "object", "description": "카카오 API 호출 실패"},
        },
    )
    def post(self, request, *args, **kwargs):
        code = request.data.get("code")

        if not code:
            raise CustomAPIException("잘못된 code 매개변수입니다.", code="missing_parameters")

        # 카카오에서 액세스 토큰 가져오기
        access_token_data = self.get_kakao_access_token(code)
        access_token = access_token_data.get("access_token")
        if not access_token:
            raise CustomAPIException("카카오에서 액세스 토큰을 가져오는 데 실패했습니다.", code="token_fetch_failed")

        # 액세스 토큰을 사용하여 사용자 정보 가져오기
        user_info = self.get_kakao_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user_data = UserInfoSerializer(user).data
        response = Response({"access_token": access_token, "user": user_data}, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")
        return response

    def get_kakao_access_token(self, code):
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_CALLBACK_URL,
            "code": code,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        response = requests.post(settings.KAKAO_TOKEN_URL, data=payload, headers=headers)
        if response.status_code != 200:
            raise CustomAPIException("카카오에서 액세스 토큰을 가져오는 데 실패했습니다.", code="token_fetch_failed")
        return response.json()

    def get_kakao_user_info(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(settings.KAKAO_USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            raise CustomAPIException(
                "카카오에서 사용자 정보를 가져오는 데 실패했습니다.", code="user_info_fetch_failed"
            )
        return response.json()

    def create_or_update_user(self, user_info):
        kakao_account = user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        name = profile.get("nickname", "")
        profile_image = profile.get("profile_image_url", "")
        email = kakao_account.get("email", "")
        phone_number = kakao_account.get("phone_number", "")

        if phone_number.startswith("+82"):
            phone_number = phone_number.replace("+82 ", "0")

        user = User.objects.filter(email=email).first() or User.objects.filter(phone_number=phone_number).first()

        if user:
            user.name = name or user.name
            user.profile_image = profile_image or user.profile_image
            if phone_number:
                user.phone_number = phone_number
        else:
            user = User(email=email, name=name, profile_image=profile_image, phone_number=phone_number)

        user.save()
        return user


class GoogleLoginCallbackAPIView(APIView):
    @extend_schema(
        tags=["Oauth"],
        summary="구글 서버인증, 액세스, 리프레시 토큰발급, 유저생성",
        request={
            "type": "object",
            "properties": {
                "code": {"type": "string", "example": "AQAAAAAA1234", "description": "Google 인증 후 반환된 코드"}
            },
            "required": ["code"],
        },
        responses={
            200: {"type": "object", "description": "로그인 성공"},
            400: {"type": "object", "description": "잘못된 요청"},
            403: {"type": "object", "description": "Google API 호출 실패"},
        },
    )
    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        if not code:
            raise CustomAPIException("잘못된 code 매개변수입니다.", code="missing_parameters")

        # Google에서 액세스 토큰 가져오기
        access_token_data = self.get_google_access_token(code)
        access_token = access_token_data.get("access_token")
        if not access_token:
            raise CustomAPIException("Google에서 액세스 토큰을 가져오는 데 실패했습니다.", code="token_fetch_failed")

        # 액세스 토큰을 사용하여 사용자 정보 가져오기
        user_info = self.get_google_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # 애플리케이션용 액세스 및 리프레시 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user_data = UserInfoSerializer(user).data
        response = Response({"access_token": access_token, "user": user_data}, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")
        return response

    def get_google_access_token(self, code):
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "code": code,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(settings.GOOGLE_TOKEN_URL, params=payload, headers=headers)
        if response.status_code != 200:
            raise CustomAPIException("Google에서 액세스 토큰을 가져오는 데 실패했습니다.", code="token_fetch_failed")
        return response.json()

    def get_google_user_info(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(settings.GOOGLE_USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            raise CustomAPIException(
                "Google에서 사용자 정보를 가져오는 데 실패했습니다.", code="user_info_fetch_failed"
            )
        return response.json()

    def create_or_update_user(self, user_info):
        try:
            email = user_info.get("email")
            name = user_info.get("name", "")
            profile_image = user_info.get("picture", "")

            user, created = User.objects.get_or_create(email=email)
            user.name = name
            user.profile_image = profile_image
            user.save()

            return user
        except Exception:
            raise CustomAPIException("사용자 생성 또는 업데이트 중 오류가 발생했습니다.", code="user_creation_error")


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Oauth"],
        summary="로그아웃 처리 (액세스 토큰 기반)",
        responses={
            200: {"type": "object", "description": "로그아웃 성공"},
            400: {"type": "object", "description": "잘못된 요청"},
            401: {"type": "object", "description": "유효하지 않거나 만료된 액세스 토큰"},
        },
    )
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise CustomAPIException("Authorization 헤더가 누락되었습니다.", code="missing_authorization_header")
        if not auth_header.startswith("Bearer "):
            raise CustomAPIException(
                "유효하지 않은 Authorization 헤더 형식입니다.", code="invalid_authorization_format"
            )

        access_token = auth_header.split(" ")[1]
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            raise CustomAPIException("사용자와 연관된 리프레시 토큰이 없습니다.", code="missing_refresh_token")

        # 리프레시 토큰 블랙리스트에 추가
        RefreshToken(refresh_token).blacklist()
        response = Response({"detail": "로그아웃에 성공했습니다."}, status=status.HTTP_200_OK)
        response.delete_cookie("refresh_token")
        return response


class RefreshAccessTokenAPIView(APIView):
    @extend_schema(
        tags=["Oauth"],
        summary="리프레시 토큰 검증 -> 새 액세스 토큰 재발급",
        responses={
            201: {"type": "object", "description": "새로운 액세스 토큰 발급"},
            400: {"type": "object", "description": "기존 액세스 토큰 유효"},
            401: {"type": "object", "description": "유효하지 않거나 만료된 리프레시 토큰"},
        },
    )
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        access_token = None
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]
        if access_token:
            try:
                AccessToken(access_token)
                raise CustomAPIException("기존 액세스 토큰이 유효합니다.", code="access_token_valid")
            except TokenError:
                pass

        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            raise CustomAPIException("리프레시 토큰이 제공되지 않았습니다.", code="missing_refresh_token")

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            return Response(
                {"detail": "새로운 액세스 토큰이 발급되었습니다.", "access_token": new_access_token},
                status=status.HTTP_201_CREATED,
            )
        except TokenError:
            raise CustomAPIException("유효하지 않거나 만료된 리프레시 토큰입니다.", code="invalid_refresh_token")
