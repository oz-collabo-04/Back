import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = f'notification_{self.user.id}'
            # 그룹에 연결
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # 비인증 유저는 연결을 거부
            await self.close()

    async def disconnect(self, close_code):
        # 그룹에서 연결 해제
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        # 알림 메시지를 클라이언트로 보냅니다
        message = event["message"]
        await self.send(text_data=json.dumps({
            "notification": message,
        }))