from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from notifications.models import Notification
from expert.models import Expert
from estimations.models import EstimationsRequest

User = get_user_model()


class NotificationAPITestCase(APITestCase):
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

        # 전문가 생성
        self.expert = Expert.objects.create(
            user=self.expert_user,
            expert_image="path/to/expert_image.jpg",
            service="mc",
            standard_charge=100000,
            available_location=["Seoul"],
            appeal="경험 많은 웨딩 전문가입니다.",
        )

        # 견적 요청 생성
        self.estimation_request = EstimationsRequest.objects.create(
            user=self.user,
            service_list=["mc"],
            prefer_gender="male",
            status="pending",
            location="Seoul",
            wedding_hall="서울 웨딩홀",
            wedding_datetime="2024-12-12 15:00:00",
        )

        # 알림 생성
        self.notification = Notification.objects.create(
            receiver=self.user,
            title="새로운 메시지",
            message="전문가로부터 새로운 메시지가 도착했습니다.",
            notification_type="message",
        )

        self.client.force_authenticate(user=self.user)

    def test_notification_list_api(self):
        # When: 알림 목록 조회 API 호출
        url = reverse("notification-list")
        response = self.client.get(url)

        # Then: 응답 상태 코드 및 데이터 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("notifications", response.data)
        self.assertIn("unread_count", response.data)

    def test_notification_detail_api(self):
        # When: 특정 알림 읽음 처리 API 호출
        url = reverse("notification-detail", args=[self.notification.id])
        response = self.client.patch(url)

        # Then: 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_notification_read_all_api(self):
        # When: 전체 알림 읽음 처리 API 호출
        url = reverse("notification-read-all")
        response = self.client.patch(url)

        # Then: 응답 상태 코드 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
