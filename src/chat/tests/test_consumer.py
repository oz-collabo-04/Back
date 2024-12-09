import asyncio

from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.urls import path
from rest_framework_simplejwt.tokens import RefreshToken

from chat.chat_consumer import ChatConsumer
from chat.models import ChatRoom, Message
from estimations.models import EstimationsRequest, Estimation
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

        self.user_access_token=str(RefreshToken.for_user(self.user).access_token)
        self.expert_user_access_token=str(RefreshToken.for_user(self.expert_user).access_token)

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

        self.estimation = Estimation.objects.create(
            expert=self.expert,
            request=self.estimation_request,
            service=self.estimation_request.service_list,
            location=self.estimation_request.location,
            due_date="2024-12-12",
            charge=150000,
        )

        # 채팅방 생성
        self.chatroom = ChatRoom.objects.create(
            user=self.user,
            expert=self.expert,
            estimation=self.estimation,
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
        user_communicator = WebsocketCommunicator(
            self.application,
            f"/ws/chat/{room_id}/",
            subprotocols=[self.user_access_token]
        )
        expert_communicator = WebsocketCommunicator(
            self.application,
            f"/ws/chat/{room_id}/",
            subprotocols=[self.expert_user_access_token]
        )
        user_communicator.scope["user"] = user
        user_communicator.scope["type"] = "websocket"

        expert_communicator.scope["user"] = expert
        expert_communicator.scope["type"] = "websocket"

        # When: user WebSocket 연결 시도
        connected, _ = await user_communicator.connect()
        assert connected

        # When: Expert WebSocket 연결 시도
        connected, _ = await expert_communicator.connect()
        assert connected

        # Then: 상대방의 입장 메시지 수신
        user_response = await asyncio.wait_for(user_communicator.receive_json_from(), timeout=5)
        self.assertEqual(user_response["type"], "announce_entered")
        self.assertEqual(user_response["message"], f"{self.expert_user.name} 님이 입장하셨습니다.")
        self.assertEqual(user_response["user_id"], self.expert_user.id)

        # When: 메시지 전송
        message_content = "Hello, World!"
        message = {"content": message_content}
        await user_communicator.send_json_to(message)

        # Then: 상대방의 메시지 수신
        expert_response = await asyncio.wait_for(expert_communicator.receive_json_from(), timeout=5)
        self.assertEqual(expert_response["type"], "chat_message")
        self.assertEqual(expert_response["content"], message['content'])
        self.assertEqual(expert_response["sender"], self.user.id)

        # Then: 나의 메시지 수신
        user_response = await asyncio.wait_for(user_communicator.receive_json_from(), timeout=5)
        self.assertEqual(user_response["type"], "chat_message")
        self.assertEqual(user_response["content"], message['content'])
        self.assertEqual(user_response["sender"], self.user.id)

        self.assertTrue(await database_sync_to_async(
            lambda: Message.objects.filter(sender=self.user, content=message['content'], room=self.chatroom).exists()
        )())

        # Finally: WebSocket 연결 종료
        await user_communicator.disconnect()
        await expert_communicator.disconnect()
