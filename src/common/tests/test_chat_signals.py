from channels.routing import URLRouter
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.test import TestCase
from django.urls import path

from chat.chat_consumer import ChatConsumer
from chat.models import ChatRoom, Message
from common.signals.chat_signals import chat_post_save_handler
from estimations.models import EstimationsRequest
from expert.models import Expert
from notifications.models import Notification

User = get_user_model()


class MessageSignalTest(TestCase):
    def setUp(self):
        # Given: 사용자와 관련 모델 초기화
        self.user = User.objects.create_user(
            email="testuser@example.com",
            name="유저",
            phone_number="01012345678",
            gender="M",
            is_active=True,
        )

        self.expert_user = User.objects.create_user(
            email="expertuser@example.com",
            name="전문가",
            phone_number="01087654321",
            gender="M",
            is_active=True,
        )

        self.client.force_login(user=self.user)
        self.client.force_login(user=self.expert_user)

        # 전문가 생성
        self.expert = Expert.objects.create(
            user=self.expert_user,
            expert_image="path/to/expert_image.jpg",
            service="mc",
            standard_charge=100000,
            available_location="seoul",
            appeal="경험 많은 웨딩 전문가입니다.",
        )

        # 견적 요청 생성
        self.estimation_request = EstimationsRequest.objects.create(
            user=self.user,
            service_list="mc",
            prefer_gender="M",
            status="pending",
            location="Seoul",
            wedding_datetime="2024-12-12",
        )

        # 채팅방 생성
        self.chatroom = ChatRoom.objects.create(
            user=self.user,
            expert=self.expert,
            request=self.estimation_request,
            user_exist=True,
            expert_exist=True,
        )

        self.application = URLRouter([path("ws/chat/<int:room_id>/", ChatConsumer.as_asgi())])

    def test_notification_created_on_message_send(self):
        # Given: 발신자가 메시지를 생성합니다.
        message_content = "안녕하세요, 이건 테스트 메시지입니다."
        Message.objects.create(room_id=1, sender=self.user, content=message_content)
        assert Notification.objects.all()

        # When: post_save 시그널이 트리거됩니다.
        # Then: 수신자를 위한 알림이 생성되어야 합니다.
        notification_exists = Notification.objects.filter(
            receiver=self.expert_user, message=message_content, notification_type="message"
        ).exists()

        self.assertTrue(notification_exists, "메시지가 전송되면 알림이 생성되어야 합니다.")
