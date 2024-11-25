from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import ChatRoom, Message
from chat.serializers.chat_serializers import ChatRoomSerializer, MessageSerializer
from estimations.models import EstimationsRequest


@extend_schema(tags=["Chat"])
class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    """
    채팅방 목록 조회 및 생성 API
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        status_filter = self.request.query_params.get("status", "all")
        valid_statuses = ["pending", "completed", "canceled"]
        user = self.request.user

        if status_filter == "all":
            return ChatRoom.objects.filter(user=user)
        elif status_filter in valid_statuses:
            estimation_requests = EstimationsRequest.objects.filter(status=status_filter, user=user)
            if estimation_requests.exists():
                return ChatRoom.objects.filter(user=user)
        else:
            return ChatRoom.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists() or request.query_params.get("status", "all") == "all":
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({"detail": "올바른 상태 값을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Chat"])
class ChatRoomDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    특정 채팅방 조회, 수정 및 삭제 API
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer
    lookup_url_kwarg = "room_id"

    def get_queryset(self):
        return ChatRoom.objects.all()

    def delete(self, request, *args, **kwargs):
        chatroom = self.get_object()
        if chatroom.user_exist or chatroom.expert_exist:
            return Response(
                {"detail": "참가자가 있는 채팅방은 삭제할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        chatroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Chat"])
class MessageListCreateAPIView(generics.ListCreateAPIView):
    """
    메시지 목록 조회 및 생성 API
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        room_id = self.kwargs.get("room_id")
        return Message.objects.filter(room_id=room_id)

    def perform_create(self, serializer):
        room_id = self.kwargs.get("room_id")
        chatroom = get_object_or_404(ChatRoom, pk=room_id)
        message = serializer.save(room=chatroom)

        # 웹소켓을 통해 메시지를 채팅방에 브로드캐스트합니다.
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room_id}", {"type": "chat_message", "message": MessageSerializer(message).data}
        )
        # 메시지 수신자에게 알림 전송 (추가 기능)
        self.send_notification(message)

    def send_notification(self, message):
        # 수신자에게 알림 전송 로직 추가
        recipient = message.recipient
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notification_{recipient.id}",
            {
                "type": "send_notification",
                "message": f"새로운 메시지가 도착했습니다: {message.content}",
            },
        )
