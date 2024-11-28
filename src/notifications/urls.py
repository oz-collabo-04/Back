from django.urls import path

from notifications.views.notification_views import NotificationListAPIView, NotificationDetailAPIView, \
    NotificationReadAllAPIView

urlpatterns = [
    path("notifications/", NotificationListAPIView.as_view(), name="notification-list"),
    path("notifications/<int:notification_id>/", NotificationDetailAPIView.as_view(), name="notification-detail"),
    path("notifications/read_all/", NotificationReadAllAPIView.as_view(), name="notification-read-all"),
]
