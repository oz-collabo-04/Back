import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.urls import path

from expert.models import Expert
from notifications.consumers import NotificationConsumer
from notifications.models import Notification

User = get_user_model()


class NotificationConsumerTest(TransactionTestCase):
    def setUp(self):
        # Given: 사용자와 관련 모델 초기화
        self.user = User.objects.create_user(
            email="testuser@example.com",
            name="유저",
            phone_number="01012345678",
            gender="male",
            is_active=True,
        )

        self.expert_user = User.objects.create_user(
            email="expertuser@example.com",
            name="전문가",
            phone_number="01087654321",
            gender="male",
            is_active=True,
        )

        # 전문가 생성
        self.expert = Expert.objects.create(
            user=self.expert_user,
            expert_image="path/to/expert_image.jpg",
            service="mc",
            standard_charge=100000,
            available_location="Seoul",
            appeal="경험 많은 웨딩 전문가입니다.",
        )

        self.application = URLRouter([path("ws/notifications/", NotificationConsumer.as_asgi())])

    @database_sync_to_async
    def create_notification(self, receiver, title, message, notification_type):
        return Notification.objects.create(
            receiver=receiver,
            title=title,
            message=message,
            notification_type=notification_type,
        )

    @database_sync_to_async
    def get_user(self, email):
        return User.objects.get(email=email)

    async def test_notification_consumer(self):
        # Given: 사용자 설정 및 WebSocket 연결
        user = await self.get_user("testuser@example.com")
        communicator = WebsocketCommunicator(self.application, "/ws/notifications/")

        communicator.scope["user"] = user
        communicator.scope["type"] = "websocket"

        # When: WebSocket 연결 시도
        connected, _ = await communicator.connect()
        assert connected

        # When: 알림 생성 및 전송
        notification = await self.create_notification(
            receiver=user,
            title="새로운 알림",
            message="테스트 알림입니다.",
            notification_type="message",
        )
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"notification_{user.id}",
            {
                "type": "send_notification",
                "notification": {
                    "title": notification.title,
                    "message": notification.message,
                    "notification_type": notification.notification_type,
                },
            },
        )

        # Then: 알림 수신 확인
        response = await communicator.receive_json_from()
        assert response["title"] == "새로운 알림"
        assert response["message"] == "테스트 알림입니다."
        assert response["notification_type"] == "message"

        # Finally: WebSocket 연결 종료
        await communicator.disconnect()
