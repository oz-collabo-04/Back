from django.urls import path

from chat.views.chat_views import (
    ChatRoomDetailAPIView,
    ChatRoomListCreateAPIView,
    ChatRoomUpdateAPIView,
    MessageListCreateAPIView,
)

urlpatterns = [
    # 채팅방 목록 조회 및 생성
    path("chatrooms/", ChatRoomListCreateAPIView.as_view(), name="chatroom-list-create"),
    # 채팅방 상세 조회 및 삭제
    path("chatrooms/<int:room_id>/", ChatRoomDetailAPIView.as_view(), name="chatroom-detail"),
    # 채팅방 나가기 - 상대방이 존재할 때 업데이트
    path("chatrooms/<int:room_id>/leave/", ChatRoomUpdateAPIView.as_view(), name="chatroom-update"),
    # 메시지 목록 조회 및 생성
    path("chatrooms/<int:room_id>/messages/", MessageListCreateAPIView.as_view(), name="message-list-create"),
]
