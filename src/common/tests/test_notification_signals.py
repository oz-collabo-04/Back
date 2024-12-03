from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from notifications.consumers import NotificationConsumer
from notifications.models import Notification

User = get_user_model()
channel_layer = get_channel_layer()


class NotificationSignalTest(TransactionTestCase):
    def setUp(self):
        # Given: 사용자와 관련 모델 초기화
        self.user = User.objects.create_user(
            email="testuser@example.com",
            name="유저",
            phone_number="01012345678",
            gender="M",
            is_active=True,
        )

    async def test_send_notification_signal(self):
        # Given: WebSocket 커뮤니케이터 설정
        communicator = WebsocketCommunicator(NotificationConsumer.as_asgi(), f"ws/notifications/{self.user.id}/")
        communicator.scope["user"] = await sync_to_async(User.objects.get)(id=self.user.id)
        connected, _ = await communicator.connect()
        self.assertTrue(connected, "WebSocket 연결에 실패했습니다.")

        # When: Notification 생성
        notification = await sync_to_async(Notification.objects.create)(
            receiver=self.user, title="새 알림", message="테스트 알림 메시지", notification_type="test", is_read=False
        )

        # Then: WebSocket을 통해 알림을 수신해야 함
        response = await communicator.receive_json_from()
        self.assertEqual(response["id"], notification.id)
        self.assertEqual(response["title"], notification.title)
        self.assertEqual(response["message"], notification.message)
        self.assertEqual(response["notification_type"], notification.notification_type)
        self.assertEqual(response["is_read"], notification.is_read)

        # Finally: WebSocket 연결 종료
        await communicator.disconnect()
