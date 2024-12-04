from django.urls import path

from users.views import user_views
from users.views.oauth_views import (
    LogoutView,
    RefreshAccessTokenAPIView,
    SocialLoginAPIView,
)

app_name = "users"
urlpatterns = [
    # oauth
    path("login/<str:provider>/callback/", SocialLoginAPIView.as_view(), name="social_login"),
    path("token/refresh/", RefreshAccessTokenAPIView.as_view(), name="refresh_token"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # user
    path("mypage/", user_views.UserEditView.as_view(), name="user_mypage"),
    path("mypage/deactivate/", user_views.UserDeactivateView.as_view(), name="user_deactivate"),
]
