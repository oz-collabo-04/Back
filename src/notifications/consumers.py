from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from common.logging_config import logger


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope["user"], AnonymousUser):
            # 비인증 유저는 연결을 거부
            await self.close()
        self.group_name = f"notification_{self.scope["user"].id}"
        # 그룹에 연결
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept(subprotocol=self.scope["subprotocols"][0])

    async def disconnect(self, close_code):
        logger.info(f"알림 웹소켓 연결 해제 - {self.group_name}")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        await self.channel_layer.group_send(self.group_name, content)

    async def send_notification(self, event):
        # 알림 메시지를 클라이언트로 보냅니다
        logger.info(f"알림을 클라이언트에 전송 : {event}")
        await self.send_json(event)
