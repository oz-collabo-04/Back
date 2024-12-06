from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from chat.models import ChatRoom

User = get_user_model()


class IsInChatRoom(BasePermission):
    """
    요청을 보낸 유저가 해당 채팅방에 존재하는지 확인하는 Permission
    """

    def has_permission(self, request, view):
        # `room_id`를 URL에서 가져오거나, 다른 경로로 가져오는 방식에 따라 수정
        room_id = view.kwargs.get("room_id")

        # 채팅방이 존재하지 않으면 404를 반환
        chat_room = get_object_or_404(ChatRoom, id=room_id)

        # 요청 보낸 사용자가 해당 채팅방에 존재하는지 확인
        return bool(chat_room.expert.user == request.user or chat_room.user == request.user)
