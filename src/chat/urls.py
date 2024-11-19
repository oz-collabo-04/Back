from django.urls import path
from chat.views.chat_views import (
    ChatRoomListCreateAPIView, ChatRoomDetailAPIView,
    MessageListCreateAPIView
)

urlpatterns = [
    path('chatrooms/', ChatRoomListCreateAPIView.as_view(), name='chatroom-list-create'),
    path('chatrooms/<int:room_id>/', ChatRoomDetailAPIView.as_view(), name='chatroom-detail'),
    path('chatrooms/<int:room_id>/messages/', MessageListCreateAPIView.as_view(), name='message-list-create'),
]
