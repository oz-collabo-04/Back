from django.urls import path

from users import oauth_views, views

app_name = "users"
urlpatterns = [
    # oauth
    path(
        "login/naver/callback/", oauth_views.NaverLoginCallbackAPIView.as_view(), name="naver_callback"
    ),  # Naver 콜백 처리
    path("login/kakao/callback/", oauth_views.KakaoLoginCallbackAPIView.as_view(), name="kakao_callback"),
    path("login/google/callback/", oauth_views.GoogleLoginCallbackAPIView.as_view(), name="google_callback"),
    path("token/refresh/", oauth_views.RefreshAccessTokenAPIView.as_view(), name="refresh_token"),
    path("logout/", oauth_views.LogoutView.as_view(), name="logout"),
    # user
    path("mypage/", views.UserEditView.as_view(), name="user_mypage"),
    path("mypage/deactivate/", views.UserDeactivateView.as_view(), name="user_deactivate"),
]
