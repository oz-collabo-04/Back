from django.urls import path

from users import views
from users.oauth_views import LogoutView, RefreshAccessTokenAPIView, SocialLoginAPIView

app_name = "users"
urlpatterns = [
    # oauth
    path("login/<str:provider>/callback/", SocialLoginAPIView.as_view(), name="social_login"),
    path("token/refresh/", RefreshAccessTokenAPIView.as_view(), name="refresh_token"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # user
    path("mypage/", views.UserEditView.as_view(), name="user_mypage"),
    path("mypage/deactivate/", views.UserDeactivateView.as_view(), name="user_deactivate"),
]
