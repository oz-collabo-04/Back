from django.urls import path
from notifications import consumers

websocket_urlpatterns = [
    path('wss/notifications/<int:user_id>/', consumers.NotificationConsumer.as_asgi()),
]