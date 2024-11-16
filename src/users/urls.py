from django.urls import path

from .views import (
    GoogleLoginCallbackAPIView,
    KakaoLoginCallbackAPIView,
    NaverLoginCallbackAPIView,
)

app_name = "users"
urlpatterns = [
    path("login/naver/callback/", NaverLoginCallbackAPIView.as_view(), name="naver_callback"),  # Naver 콜백 처리
    path("login/kakao/callback/", KakaoLoginCallbackAPIView.as_view(), name="kakao_callback"),
    path("login/google/callback/", GoogleLoginCallbackAPIView.as_view(), name="google_callback"),
]
