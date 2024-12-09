from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import ChatRoom, Message
from chat.serializers.chat_serializers import ChatRoomSerializer, MessageSerializer
from common.exceptions import BadRequestException
from common.permissions.chat_permissions import IsInChatRoom


class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        status = self.request.query_params.get("status")
        valid_statuses = ["pending", "reserved"]
        user = self.request.user

        if status:
            if status in valid_statuses:
                if status == valid_statuses[0]:
                    chatrooms = ChatRoom.objects.filter(
                        Q(user=user, user_exist=True) | Q(expert__user=user, expert_exist=True),
                        estimation__reservation__isnull=True
                    )
                    return chatrooms

                chatrooms = ChatRoom.objects.filter(
                    Q(user=user, user_exist=True) | Q(expert__user=user, expert_exist=True),
                    estimation__reservation__isnull=False
                )
                return chatrooms

            else:
                raise BadRequestException(
                    "쿼리 파라미터의 값이 유효하지 않습니다. choice in ['reserved', 'pending']"
                )

        return ChatRoom.objects.filter(
                    Q(user=user, user_exist=True) | Q(expert__user=user, expert_exist=True)
                )



    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=["Chat"],
        summary="유저가 마음에 드는 견적이 있으면 채팅방을 생성, 이미 채팅방이 존재하면 기존 채팅방을 내려줌."
    )
    def post(self, request, *args, **kwargs):
        expert_id = request.data.get("expert_id")
        estimation_id = request.data.get("estimation_id")
        try:
            chatroom = ChatRoom.objects.get(
                expert_id=expert_id,
                estimation_id=estimation_id,
                user=self.request.user,
            )
            serializer = self.get_serializer(chatroom)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except ChatRoom.DoesNotExist:
            return self.create(request, *args, **kwargs)

    @extend_schema(
        tags=["Chat"],
        summary="채팅방 조회 및 쿼리파라미터로 필터링 조회",
        parameters=[
            OpenApiParameter(
                name="status",
                description="예약의 상태로 채팅방 리스트를 필터링 합니다. 사용가능한 status - 'reserved', 'pending')",
                required=False,
                type=str,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ChatRoomDetailAPIView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsInChatRoom]
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
            if request.user == chatroom.user:
                chatroom.user_exist = False
            elif request.user == chatroom.expert.user:
                chatroom.expert_exist = False
            chatroom.save()
        # 상대방중 한명이라도 없으면 채팅방 삭제
        else:
            chatroom.delete()
        return Response({"detail": "채팅방 나가기에 성공하였습니다."}, status=status.HTTP_200_OK)

    @extend_schema(tags=["Chat"])
    def get(self, request, *args, **kwargs):
        """
        채팅방 상세정보 조회
        """
        return self.retrieve(request, *args, **kwargs)


@extend_schema(tags=["Chat"])
class MessageListCreateAPIView(generics.ListAPIView):
    """
    메시지 목록 조회 API
    """

    permission_classes = [IsAuthenticated, IsInChatRoom]
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    lookup_url_kwarg = "room_id"

    def get_queryset(self):
        message = self.queryset.filter(room_id=self.kwargs[self.lookup_url_kwarg]).order_by("timestamp")
        return message
