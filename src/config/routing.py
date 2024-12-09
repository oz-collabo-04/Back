from django.urls import path

from chat.chat_consumer import ChatConsumer
from notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    path("ws/chat/<int:room_id>/", ChatConsumer.as_asgi()),
]
