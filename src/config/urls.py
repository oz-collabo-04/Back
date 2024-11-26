from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/experts/", include("expert.urls")),
    path("api/v1/experts/reviews/", include("reviews.urls.expert_urls")),
    path("api/v1/experts/estimations/", include("estimations.urls.expert_urls")),
    path("api/v1/estimations/", include("estimations.urls.guest_urls")),
    path("api/v1/reservations/", include("reservations.urls")),
    path("api/v1/reviews/", include("reviews.urls.guest_urls")),
    path("api/v1/chat/", include("chat.urls")),
    path("api/v1/notifications/", include("notifications.urls")),
    path("api/v1/services/", include("common.urls")),
]


if settings.DEBUG:
    urlpatterns += [
        path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
        path("api/v1/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
        path("api/v1/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    ]
