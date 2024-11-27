from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import ChatRoom, Message
from chat.serializers.chat_serializers import (
    ChatRoomSerializer,
    ChatroomUpdateSerializer,
    MessageSerializer,
)
from common.exceptions import BadRequestException


@extend_schema(tags=["Chat"])
class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    """
    채팅방 목록 조회 및 생성 API
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        status_filter = self.request.query_params.get("status")
        valid_statuses = ["pending", "completed", "canceled"]
        user = self.request.user

        if status_filter:
            if status_filter in valid_statuses:
                chatrooms = ChatRoom.objects.filter(
                    Q(request__user=user) | Q(expert__user=user),
                    reqeust__status__in=status_filter,
                )
                return chatrooms

            else:
                raise BadRequestException(
                    "쿼리 파라미터의 값이 유효하지 않습니다. choice in ['pending', 'completed', 'canceled']"
                )

        chatrooms = ChatRoom.objects.filter(Q(request__user=user) | Q(expert__user=user))
        return chatrooms

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatRoomDetailAPIView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer
    lookup_field = "id"
    lookup_url_kwarg = "room_id"
    queryset = ChatRoom.objects.all()

    @extend_schema(tags=["Chat"])
    def delete(self, request, *args, **kwargs):
        """
        채팅방 나가기 - 상대방이 없는 경우(완전 삭제)
        """
        chatroom = self.get_object()
        if chatroom.user_exist and chatroom.expert_exist:
            return Response(
                {"detail": "참가자가 있는 채팅방은 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        chatroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["Chat"])
    def get(self, request, *args, **kwargs):
        """
        채팅방 상세정보 조회
        """
        return self.retrieve(request, *args, **kwargs)


@extend_schema(tags=["Chat"])
class ChatRoomUpdateAPIView(generics.GenericAPIView, mixins.UpdateModelMixin):
    """
    채팅방 나가기 - 상대방이 존재할 때
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChatroomUpdateSerializer
    lookup_field = "id"
    lookup_url_kwarg = "room_id"
    queryset = ChatRoom.objects.all()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@extend_schema(tags=["Chat"])
class MessageListCreateAPIView(generics.ListAPIView):
    """
    메시지 목록 조회 및 생성 API
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        room_id = self.kwargs.get("room_id")
        return Message.objects.filter(room_id=room_id)
