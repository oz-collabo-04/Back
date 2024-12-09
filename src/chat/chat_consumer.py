from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db.models import Q

from chat.models import ChatRoom, Message
from common.logging_config import logger


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            # URL에서 채팅방 ID 가져오기
            self.room_id = self.scope["url_route"]["kwargs"].get("room_id")
            logger.info(self.scope)
            logger.info(f"request room_id: {self.room_id}")

            if not self.room_id:
                logger.warning(f"Invalid room_id: {self.room_id}")
                await self.close(code=4001)  # 클라이언트에 에러 코드 전달
                return

            if not self.validate_user_in_chatroom(self.scope["user"], self.room_id):
                await self.close(code=4001, reason="user not in this chatroom.")

            self.room_group_name = f"chat_{self.room_id}"

            # 인증 확인
            if isinstance(self.scope["user"], AnonymousUser):
                logger.warning("Unauthorized WebSocket connection attempt.")
                await self.close(code=4003)  # 클라이언트에 권한 없음 코드 전달
                return

            # 그룹에 WebSocket 연결 추가
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            # WebSocket 연결 수락
            await self.accept(subprotocol=self.scope["subprotocols"][0])

            # 내가 채팅방에 들어왔음을 상대방에게 알림
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "announce_entered",
                    "message": f"{self.scope["user"].name} 님이 입장하셨습니다.",
                    "user_id": self.scope["user"].id,
                },
            )

            await database_sync_to_async(
                lambda: Message.objects.exclude(sender_id=self.scope["user"].id)
                .filter(is_read=False, room_id=self.room_id)
                .update(is_read=True)
            )()

            # 디버깅 로그
            logger.info(f"WebSocket connected to room: {self.room_group_name} (channel: {self.channel_layer})")
        except Exception as e:
            # 예외 처리 및 로그 출력
            logger.error(f"Error during WebSocket connection: {e}")
            await self.close()

    async def receive_json(self, content, **kwargs):
        logger.info(f"WebSocket received data: {content}, type: {type(content)}")
        if content.get("type") == "announce_exist":
            await self.channel_layer.group_send(self.room_group_name, content)
            return
        try:
            if not content.get("content"):
                await self.empty_error("채팅 메시지는 공백일 수 없습니다.")

            content["sender_id"] = self.scope["user"].id
            # message save to db
            message = await database_sync_to_async(Message.objects.create)(room_id=self.room_id, **content)
            content["sender"] = content.pop("sender_id")
            content["timestamp"] = str(message.timestamp)
            content["type"] = "chat_message"

            await self.channel_layer.group_send(self.room_group_name, content)
        except Exception as e:
            # 에러 로그 출력 (필요 시 로그 저장 가능)
            logger.error(f"Error in receive_json: {e}")
            # 에러 메시지 클라이언트로 전송 (선택 사항)
            await self.send_json({"error": "Message delivery failed."})

    async def empty_error(self, detail):
        await self.send_json({"type": "empty_error", "detail": detail})

    async def disconnect(self, code):
        logger.info(f"socket closed. - {code}")
        # 상대방에게 채팅방에서 연결이 해제되었음을 알림 -> 나가기랑 별도.
        if not isinstance(self.scope["user"], AnonymousUser):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_exited",
                    "exit_user": self.scope["user"].id,
                    "message": f"{self.scope["user"].name} 님의 연결이 해제되었습니다.",
                },
            )
        # 그룹에서 제거
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_message(self, content, **kwargs):
        logger.info(f"chat_message received data: {content}, type: {type(content)}")
        await self.send_json(content)

    async def announce_entered(self, content, **kwargs):
        logger.info(f"announce_entered received data: {content}, type: {type(content)}")
        if content["user_id"] == self.scope["user"].id:
            return
        await self.send_json(content)

    async def chat_exited(self, content, **kwargs):
        logger.info(f"chat_exited received data: {content}, type: {type(content)}")
        if content["exit_user"] == self.scope["user"].id:
            return
        await self.send_json(content)

    async def announce_exist(self, content, **kwargs):
        logger.info(f"announce_exist received data: {content}, type: {type(content)}")
        if content["user_id"] == self.scope["user"].id:
            return
        await self.send_json(content)

    @database_sync_to_async
    def validate_user_in_chatroom(self, user, room_id):
        try:
            chatroom = ChatRoom.objects.get(pk=room_id)
            if not chatroom.user == user or not chatroom.expert.user:
                return False
            return True
        except ChatRoom.DoesNotExist:
            self.close(code=1011, reason="chatroom not found.")
