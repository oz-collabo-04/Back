import asyncio

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.urls import path

from chat.chat_consumer import ChatConsumer
from chat.models import ChatRoom, Message
from estimations.models import EstimationsRequest
from expert.models import Expert

User = get_user_model()


class ChatConsumerTransactionTest(TransactionTestCase):
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

        self.client.force_login(user=self.user)
        self.client.force_login(user=self.expert_user)

        # 전문가 생성
        self.expert = Expert.objects.create(
            user=self.expert_user,
            expert_image="path/to/expert_image.jpg",
            service="mc",
            standard_charge=100000,
            available_location="Seoul",
            appeal="경험 많은 웨딩 전문가입니다.",
        )

        # 견적 요청 생성
        self.estimation_request = EstimationsRequest.objects.create(
            user=self.user,
            service_list="mc",
            prefer_gender="male",
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

    @database_sync_to_async
    def get_user(self, email):
        return User.objects.get(email=email)

    async def test_chat_consumer_transaction(self):
        # Given: 사용자와 방 ID 설정
        user = await self.get_user("testuser@example.com")
        expert = await self.get_user("expertuser@example.com")

        room_id = self.chatroom.id
        user_communicator = WebsocketCommunicator(self.application, f"/ws/chat/{room_id}/")
        expert_communicator = WebsocketCommunicator(self.application, f"/ws/chat/{room_id}/")
        user_communicator.scope["user"] = user
        user_communicator.scope["type"] = "websocket"

        expert_communicator.scope["user"] = expert
        expert_communicator.scope["type"] = "websocket"

        # When: WebSocket 연결 시도
        connected, _ = await user_communicator.connect()
        assert connected

        connected, _ = await expert_communicator.connect()
        assert connected

        # Given: 메시지 전송
        message_content = "Hello, World!"
        message = {"content": message_content}
        await user_communicator.send_json_to(message)

        # Then: 메시지 수신 확인
        try:
            user_response = await asyncio.wait_for(user_communicator.receive_json_from(), timeout=5)
            expert_response = await asyncio.wait_for(expert_communicator.receive_json_from(), timeout=5)

            self.assertEqual(user_response["type"], "chat_message")
            self.assertEqual(user_response["content"], message_content)
            self.assertEqual(user_response["sender_id"], user.id)

            self.assertEqual(expert_response["type"], "chat_message")
            self.assertEqual(expert_response["content"], message_content)
            self.assertEqual(expert_response["sender_id"], user.id)
        except asyncio.TimeoutError:
            self.fail("WebSocket에서 메시지를 받는 데 실패했습니다 (타임아웃 발생).")

        # Finally: WebSocket 연결 종료
        await user_communicator.disconnect()
        await expert_communicator.disconnect()
