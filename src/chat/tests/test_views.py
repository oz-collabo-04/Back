from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from chat.models import ChatRoom, Message
from estimations.models import Estimation, EstimationsRequest
from expert.models import Expert

User = get_user_model()


class ChatAPITestCase(TestCase):
    def setUp(self):
        # Given: 사용자와 관련 모델 초기화
        self.client = APIClient()

        # 사용자 생성
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

        self.client.force_authenticate(user=self.user)

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

        self.estimation_request2 = EstimationsRequest.objects.create(
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

        self.estimation2 = Estimation.objects.create(
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

        # 메시지 생성
        self.message = Message.objects.create(
            room=self.chatroom,
            sender=self.user,
            content="안녕하세요!",
        )

    def test_list_chatrooms(self):
        # When: 채팅방 목록 조회
        url = reverse("chatroom-list-create")
        response = self.client.get(url)

        # Then: 응답 상태와 데이터 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.chatroom.id)

    def test_create_chatroom(self):
        # When: 새로운 채팅방 생성
        url = reverse("chatroom-list-create")
        data = {"expert_id": self.expert.id, "estimation_id": self.estimation2.id}
        response = self.client.post(url, data)

        # Then: 채팅방 생성 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ChatRoom.objects.filter(user=self.user, expert=self.expert).exists())

    def test_get_chatroom_detail(self):
        # When: 특정 채팅방 조회
        url = reverse("chatroom-detail", kwargs={"room_id": self.chatroom.id})
        response = self.client.get(url)

        # Then: 응답 상태와 데이터 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.chatroom.id)

    def test_delete_chatroom_with_participants(self):
        # Given: 참가자가 있는 채팅방
        self.chatroom.expert_exist = True
        self.chatroom.save()

        # When: 채팅방 삭제 요청
        url = reverse("chatroom-detail", kwargs={"room_id": self.chatroom.id})
        response = self.client.delete(url)

        # Then: 채팅방 유저의 상태 변경 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.chatroom.refresh_from_db()
        self.assertFalse(self.chatroom.user_exist)

    def test_delete_other_empty_chatroom(self):
        # Given: 참가자가 없는 채팅방
        self.chatroom.expert_exist = False
        self.chatroom.save()

        # When: 참가자가 없는 채팅방 삭제 요청
        url = reverse("chatroom-detail", kwargs={"room_id": self.chatroom.id})
        response = self.client.delete(url)

        # Then: 삭제 성공 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(ChatRoom.objects.filter(id=self.chatroom.id).exists())

    def test_list_messages(self):
        # When: 채팅방 메시지 조회
        url = reverse("message-list-create", kwargs={"room_id": self.chatroom.id})
        response = self.client.get(url)

        # Then: 메시지 목록 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], self.message.content)
