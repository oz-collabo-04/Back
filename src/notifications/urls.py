from django.urls import path

from notifications.views.notification_views import (
    NotificationDetailAPIView,
    NotificationListAPIView,
    NotificationReadAllAPIView,
)

urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path("<int:notification_id>/", NotificationDetailAPIView.as_view(), name="notification-detail"),
    path("read_all/", NotificationReadAllAPIView.as_view(), name="notification-read-all"),
]
