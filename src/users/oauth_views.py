import logging

import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from users.models import User


# #### 소셜 로그인 / 네이버, 카카오, 구글/
# 네이버, 카카오는 이메일과 전화번호로 검증으로 유저 중복생성을 최소화습니다.
# 구글은 전화번호를 받아오지 않기때문에 이메일이 다르면 유저 중복생성을 막을 수가 없네?요..;.
class NaverLoginCallbackAPIView(APIView):
    @extend_schema(
        tags=["oauth-back"],
        parameters=[
            OpenApiParameter("code", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("state", OpenApiTypes.STR, OpenApiParameter.QUERY),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "example": "c8ceMEjfnorlQwEisqemfpM1Wzw7aGp7JnipglQipkOn5Zp7...",
                    }
                },
            }
        },
    )
    def get(self, request, *args, **kwargs):
        # 네이버에서 code와 state 매개변수로 리디렉션될 때 처리
        code = request.GET.get("code")
        state = request.GET.get("state")

        # code 또는 state가 없는 경우 예외 발생
        if not code or not state:
            raise PermissionDenied("잘못된 code 또는 state 매개변수입니다.")

        # 네이버로부터 액세스 토큰을 가져오는 함수 호출
        access_token_data = self.get_naver_access_token(code, state)
        access_token = access_token_data.get("access_token")
        if not access_token:
            raise PermissionDenied("네이버에서 액세스 토큰을 가져오는데 실패했습니다.")

        # 가져온 액세스 토큰을 사용하여 사용자 정보 가져오기
        user_info = self.get_naver_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # 애플리케이션용 리프레시 토큰 생성
        refresh = RefreshToken.for_user(user)
        # 애플리케이션용 액세스 토큰 생성
        access_token = str(AccessToken.for_user(user))

        # 액세스 토큰을 응답 본문에 반환하고 리프레시 토큰을 쿠키로 설정
        response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", str(refresh), httponly=True, secure=True, samesite="Lax")
        return response

    @extend_schema(
        tags=["Oauth"],
        parameters=[
            OpenApiParameter("code", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("state", OpenApiTypes.STR, OpenApiParameter.QUERY),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "example": "c8ceMEjfnorlQwEisqemfpM1Wzw7aGp7JnipglQipkOn5Zp7...",
                    }
                },
            }
        },
    )
    def post(self, request, *args, **kwargs):
        # 네이버에서 code와 state 매개변수로 리디렉션될 때 처리
        code = request.data.get("code")
        state = request.data.get("state")

        # code 또는 state가 없는 경우 예외 발생
        if not code or not state:
            raise PermissionDenied("잘못된 code 또는 state 매개변수입니다.")

        # 네이버로부터 액세스 토큰을 가져오는 함수 호출
        access_token_data = self.get_naver_access_token(code, state)
        access_token = access_token_data.get("access_token")
        if not access_token:
            raise PermissionDenied("네이버에서 액세스 토큰을 가져오는데 실패했습니다.")

        # 가져온 액세스 토큰을 사용하여 사용자 정보 가져오기
        user_info = self.get_naver_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # 애플리케이션용 리프레시 토큰 생성
        refresh = RefreshToken.for_user(user)
        # 애플리케이션용 액세스 토큰 생성
        access_token = str(AccessToken.for_user(user))

        # 액세스 토큰을 응답 본문에 반환하고 리프레시 토큰을 쿠키로 설정
        response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
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
        if response.status_code != 200:
            raise PermissionDenied(f"네이버에서 액세스 토큰을 가져오는 데 실패했습니다. 상세 정보: {response.text}")
        return response.json()

    def get_naver_user_info(self, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(settings.NAVER_USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            raise PermissionDenied(f"네이버에서 사용자 정보를 가져오는 데 실패했습니다. 상세 정보: {response.text}")
        return response.json()

    def create_or_update_user(self, user_info):
        response_data = user_info.get("response", {})
        name = response_data.get("name", "네이버 사용자")
        email = response_data.get("email")
        profile_image = response_data.get("profile_image")
        gender = response_data.get("gender", "unknown")
        phone_number = response_data.get("mobile")

        user = User.objects.filter(email=email).first() or User.objects.filter(phone_number=phone_number).first()
        if user:
            user.name = name or user.name
            user.profile_image = profile_image or user.profile_image
            user.gender = gender or user.gender
            if phone_number:
                user.phone_number = phone_number
        else:
            user = User(email=email, name=name, profile_image=profile_image, gender=gender, phone_number=phone_number)

        user.save()
        return user


class KakaoLoginCallbackAPIView(APIView):
    @extend_schema(
        tags=["oauth-back"],
        parameters=[OpenApiParameter("code", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "array",
                        "example": "c8ceMEjfnorlQwEisqemfpM1Wzw7aGp7JnipglQipkOn5Zp3tyP7dHQoP0zNKHUq2gY",
                    }
                },
            }
        },
    )
    def get(self, request, *args, **kwargs):
        # 카카오에서 `code` 매개변수로 리디렉션되었을 때 처리
        code = request.GET.get("code")

        # code가 없는 경우 예외 발생
        if not code:
            raise PermissionDenied("잘못된 code 매개변수입니다.")

        # 카카오로부터 액세스 토큰 가져오기
        access_token_data = self.get_kakao_access_token(code)
        access_token = access_token_data.get("access_token")
        if not access_token:
            raise PermissionDenied("카카오에서 액세스 토큰을 가져오는데 실패했습니다.")

        # 액세스 토큰을 사용하여 사용자 정보 가져오기
        user_info = self.get_kakao_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # 애플리케이션용 액세스 및 리프레시 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # 액세스 토큰을 응답 본문에 반환하고 리프레시 토큰을 쿠키로 설정
        response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")
        return response

    @extend_schema(
        tags=["Oauth"],
        parameters=[OpenApiParameter("code", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "array",
                        "example": "c8ceMEjfnorlQwEisqemfpM1Wzw7aGp7JnipglQipkOn5Zp3tyP7dHQoP0zNKHUq2gY",
                    }
                },
            }
        },
    )
    def post(self, request, *args, **kwargs):
        # 카카오에서 `code` 매개변수로 리디렉션되었을 때 처리
        code = request.data.get("code")

        # code가 없는 경우 예외 발생
        if not code:
            raise PermissionDenied("잘못된 code 매개변수입니다.")

        # 카카오로부터 액세스 토큰 가져오기
        access_token_data = self.get_kakao_access_token(code)
        access_token = access_token_data.get("access_token")
        if not access_token:
            raise PermissionDenied("카카오에서 액세스 토큰을 가져오는데 실패했습니다.")

        # 액세스 토큰을 사용하여 사용자 정보 가져오기
        user_info = self.get_kakao_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # 애플리케이션용 액세스 및 리프레시 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # 액세스 토큰을 응답 본문에 반환하고 리프레시 토큰을 쿠키로 설정
        response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")
        return response

    def get_kakao_access_token(self, code):
        # 카카오에 액세스 토큰 요청을 위한 페이로드 설정
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_CALLBACK_URL,
            "code": code,
        }

        # 카카오로 POST 요청 보내기
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        response = requests.post(settings.KAKAO_TOKEN_URL, data=payload, headers=headers)
        if response.status_code != 200:
            print(response.json())
            raise PermissionDenied("카카오에서 액세스 토큰을 가져오는 데 실패했습니다.")

        return response.json()

    def get_kakao_user_info(self, access_token):
        # 카카오 사용자 정보를 가져오기 위한 헤더 설정
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        # 카카오 사용자 정보 API 호출
        response = requests.get(settings.KAKAO_USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            print(response.json())
            raise PermissionDenied("카카오에서 사용자 정보를 가져오는 데 실패했습니다.")

        return response.json()

    def create_or_update_user(self, user_info):
        # 카카오 사용자 정보에서 필요한 필드 추출
        kakao_account = user_info.get("kakao_account", {})
        profile = kakao_account.get("profile", {})
        name = profile.get("nickname", "")  # 카카오 API에 따라 'nickname' 또는 'name' 사용
        profile_image = profile.get("profile_image_url", "")  # 프로필 이미지 (필수 동의)
        email = kakao_account.get("email", "")  # 카카오 계정(이메일) (필수 동의)
        gender = kakao_account.get("gender", "")  # 성별 (필수 동의)
        phone_number = kakao_account.get("phone_number", "")  # 전화번호 (필수 동의)

        # 전화번호 변환 로직
        if phone_number.startswith("+82"):
            phone_number = phone_number.replace("+82 ", "0")

        # 이메일 또는 전화번호가 있는지 확인하여 기존 사용자 검색
        user = User.objects.filter(email=email).first() or User.objects.filter(phone_number=phone_number).first()

        if user:
            # 사용자 정보 업데이트
            user.name = name or user.name  # 이름이 제공되지 않으면 기존 이름 유지
            user.profile_image = profile_image or user.profile_image  # 프로필 이미지가 제공되지 않으면 기존 이미지 유지
            if phone_number:
                user.phone_number = phone_number  # 전화번호가 있으면 업데이트
        else:
            # 새로운 사용자 생성
            user = User(email=email, name=name, profile_image=profile_image, phone_number=phone_number, gender=gender)

        user.save()
        return user


class GoogleLoginCallbackAPIView(APIView):
    @extend_schema(
        tags=["oauth-back"],
        parameters=[OpenApiParameter("code", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={
            200: {"type": "object", "properties": {"access_token": {"type": "string", "example": "ya29.a0AfH6SMC..."}}}
        },
    )
    def get(self, request, *args, **kwargs):
        # Google에서 `code` 매개변수로 리디렉션되었을 때 처리
        code = request.GET.get("code")

        # code가 없는 경우 예외 발생
        if not code:
            raise PermissionDenied("잘못된 code 매개변수입니다.")

        # Google로부터 액세스 토큰 가져오기
        access_token_data = self.get_google_access_token(code)
        access_token = access_token_data.get("access_token")
        if not access_token:
            print(access_token_data.get("error"))
            raise PermissionDenied("Google에서 액세스 토큰을 가져오는 데 실패했습니다.")

        # 액세스 토큰을 사용하여 사용자 정보 가져오기
        user_info = self.get_google_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # 애플리케이션용 액세스 및 리프레시 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # 액세스 토큰을 응답 본문에 반환하고 리프레시 토큰을 쿠키로 설정
        response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")
        return response

    @extend_schema(
        tags=["Oauth"],
        parameters=[OpenApiParameter("code", OpenApiTypes.STR, OpenApiParameter.QUERY)],
        responses={
            200: {"type": "object", "properties": {"access_token": {"type": "string", "example": "ya29.a0AfH6SMC..."}}}
        },
    )
    def post(self, request, *args, **kwargs):
        # Google에서 `code` 매개변수로 리디렉션되었을 때 처리
        code = request.data.get("code")

        # code가 없는 경우 예외 발생
        if not code:
            raise PermissionDenied("잘못된 code 매개변수입니다.")

        # Google로부터 액세스 토큰 가져오기
        access_token_data = self.get_google_access_token(code)
        access_token = access_token_data.get("access_token")
        if not access_token:
            print(access_token_data.get("error"))
            raise PermissionDenied("Google에서 액세스 토큰을 가져오는 데 실패했습니다.")

        # 액세스 토큰을 사용하여 사용자 정보 가져오기
        user_info = self.get_google_user_info(access_token)
        user = self.create_or_update_user(user_info)

        # 애플리케이션용 액세스 및 리프레시 토큰 생성
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # 액세스 토큰을 응답 본문에 반환하고 리프레시 토큰을 쿠키로 설정
        response = Response({"access_token": access_token}, status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", refresh_token, httponly=True, secure=True, samesite="Lax")
        return response

    def get_google_access_token(self, code):
        # Google에 액세스 토큰 요청을 위한 페이로드 설정
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "code": code,
        }

        # Google로 POST 요청 보내기
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(settings.GOOGLE_TOKEN_URL, params=payload, headers=headers)
        if response.status_code != 200:
            print(response.json().get("error"))
            raise PermissionDenied("Google에서 액세스 토큰을 가져오는 데 실패했습니다.")

        return response.json()

    def get_google_user_info(self, access_token):
        # Google 사용자 정보를 가져오기 위한 헤더 설정
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        # Google 사용자 정보 API 호출
        response = requests.get(settings.GOOGLE_USER_INFO_URL, headers=headers)
        if response.status_code != 200:
            raise PermissionDenied("Google에서 사용자 정보를 가져오는 데 실패했습니다.")

        return response.json()

    def create_or_update_user(self, user_info):
        # Google 사용자 정보에서 필요한 필드 추출
        email = user_info.get("email")
        name = user_info.get("name", "")
        profile_image = user_info.get("picture", "")
        # 추가적인 필드를 처리할 수 있습니다.

        # 사용자 생성 또는 업데이트
        user, created = User.objects.get_or_create(email=email)
        user.name = name
        user.profile_image = profile_image
        user.save()

        return user


# Logger 설정
logger = logging.getLogger(__name__)


#### 로그아웃
class LogoutView(APIView):
    """
    로그아웃 처리 (액세스 토큰 및 리프레시 토큰 무효화)
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User_Mypage"],
        summary="로그아웃 처리 (액세스 토큰 기반)",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "로그아웃에 성공했습니다. 모든 리프레시 토큰이 무효화되었습니다.",
                    },
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "Authorization 헤더가 누락되었습니다."},
                },
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "유효하지 않거나 만료된 액세스 토큰입니다."},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        """
        POST 요청으로 로그아웃 처리
        """
        # Authorization 헤더에서 액세스 토큰 가져오기
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logger.warning("Authorization 헤더가 누락되었습니다.")
            return Response(
                {"detail": "Authorization 헤더가 누락되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not auth_header.startswith("Bearer "):
            logger.warning("유효하지 않은 Authorization 헤더 형식: %s", auth_header)
            return Response(
                {"detail": "유효하지 않은 Authorization 헤더 형식입니다. 'Bearer'로 시작해야 합니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = auth_header.split(" ")[1]

        try:
            # 액세스 토큰 디코딩 및 사용자 ID 가져오기
            decoded_access_token = AccessToken(access_token)
            user_id = decoded_access_token["user_id"]
            logger.info("사용자 ID %s로부터 로그아웃 요청 수신.", user_id)

            # 리프레시 토큰 가져오기
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                logger.warning("사용자와 연관된 리프레시 토큰이 없습니다.")
                return Response(
                    {"detail": "사용자와 연관된 리프레시 토큰이 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 리프레시 토큰 블랙리스트에 추가
            try:
                RefreshToken(refresh_token).blacklist()
                logger.info("리프레시 토큰이 블랙리스트에 성공적으로 등록되었습니다.")
            except Exception as e:
                logger.error("리프레시 토큰 블랙리스트 등록 실패: %s", str(e))
                return Response(
                    {"detail": f"리프레시 토큰 블랙리스트 등록 실패: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # 쿠키에서 리프레시 토큰 삭제
            response = Response(
                {"detail": "로그아웃에 성공했습니다. 모든 리프레시 토큰이 무효화되었습니다."},
                status=status.HTTP_200_OK,
            )
            response.delete_cookie("refresh_token")
            logger.info("사용자 ID %s의 로그아웃이 완료되었습니다.", user_id)
            return response

        except TokenError as e:
            logger.warning("유효하지 않거나 만료된 액세스 토큰: %s", str(e))
            return Response(
                {"detail": "유효하지 않거나 만료된 액세스 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            logger.error("로그아웃 처리 중 예외 발생: %s", str(e))
            return Response(
                {"detail": f"오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ### 리프레시 토큰 검증후 액세스토큰 재발급
class RefreshAccessTokenAPIView(APIView):
    """
    쿠키에 저장된 리프레시 토큰을 검증하여
    새 액세스 토큰을 발급하거나 401 오류를 반환하는 API.
    """

    @extend_schema(
        tags=["Oauth"],
        summary="리프레시 토큰 검증 -> 새 액세스 토큰 재발급",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "새로운 액세스 토큰이 발급되었습니다."},
                    "access_token": {"type": "string", "example": "new_access_token_example"},
                },
            },
            401: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "유효하지 않거나 만료된 리프레시 토큰입니다."},
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "example": "리프레시 토큰이 제공되지 않았습니다."},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        """
        POST 요청으로 쿠키에 저장된 리프레시 토큰 검증 후 새로운 액세스 토큰 발급.
        """
        # 쿠키에서 리프레시 토큰 가져오기
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            logger.warning("리프레시 토큰이 제공되지 않았습니다.")
            return Response(
                {"detail": "리프레시 토큰이 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 리프레시 토큰 검증 및 새로운 액세스 토큰 생성
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            logger.info("새로운 액세스 토큰이 발급되었습니다.")

            return Response(
                {
                    "detail": "새로운 액세스 토큰이 발급되었습니다.",
                    "access_token": new_access_token,
                },
                status=status.HTTP_200_OK,
            )
        except TokenError as e:
            logger.warning("유효하지 않거나 만료된 리프레시 토큰: %s", str(e))
            return Response(
                {"detail": "유효하지 않거나 만료된 리프레시 토큰입니다."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            logger.error("리프레시 토큰 검증 중 예외 발생: %s", str(e))
            return Response(
                {"detail": "오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
