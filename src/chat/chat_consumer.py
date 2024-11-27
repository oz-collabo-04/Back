from channels.generic.websocket import AsyncJsonWebsocketConsumer

from common.logging_config import logger


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            # URL에서 채팅방 ID 가져오기
            self.room_id = self.scope["url_route"]["kwargs"].get("room_id")
            if not self.room_id:
                logger.info(f"Invalid room_id: {self.room_id}")
                await self.close(code=4001)  # 클라이언트에 에러 코드 전달
                return

            self.room_group_name = f"chat_{self.room_id}"

            # 인증 확인
            if not self.scope["user"].is_authenticated:
                logger.info("Unauthorized WebSocket connection attempt.")
                await self.close(code=4003)  # 클라이언트에 권한 없음 코드 전달
                return

            # 그룹에 WebSocket 연결 추가
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            # WebSocket 연결 수락
            await self.accept()

            # 디버깅 로그
            logger.info(f"WebSocket connected to room: {self.room_group_name} (channel: {self.channel_name})")
        except Exception as e:
            # 예외 처리 및 로그 출력
            logger.error(f"Error during WebSocket connection: {e}")
            await self.close()

    async def receive_json(self, content, **kwargs):
        try:
            message = content.get("message", "")
            email = content.get("email", "Anonymous")

            if not message or not email:
                await self.send_json({"error": "Invalid data received."})
                return

            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message", "message": message, "email": email}
            )
        except Exception as e:
            # 에러 로그 출력 (필요 시 로그 저장 가능)
            logger.error(f"Error in receive_json: {e}")
            # 에러 메시지 클라이언트로 전송 (선택 사항)
            await self.send_json({"error": "Message delivery failed."})

    async def disconnect(self, code):
        # 그룹에서 제거
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def chat_message(self, content, **kwargs):
        message = content.get("message", "")
        email = content.get("email", "Anonymous")
        await self.send_json(
            {
                "type": "chat_message",
                "message": message,
                "email": email,
            }
        )
