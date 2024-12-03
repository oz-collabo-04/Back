from django.contrib.auth import get_user_model
from django.test import TestCase

import common.signals  # 시그널을 명시적으로 등록
from estimations.models import Estimation, EstimationsRequest
from expert.models import Career, Expert
from notifications.models import Notification

User = get_user_model()


class EstimationRequestNotificationSignalTest(TestCase):
    def setUp(self):
        # Given: 사용자와 전문가 초기화
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
            is_expert=True,
        )

        # 전문가 생성
        self.expert = Expert.objects.create(
            user=self.expert_user,
            expert_image="path/to/expert_image.jpg",
            service="mc",
            standard_charge=100000,
            available_location="seoul",
            appeal="경험 많은 웨딩 전문가입니다.",
        )

    def test_notification_created_on_estimations_request_creation(self):
        # Given: EstimationsRequest 생성
        estimation_request = EstimationsRequest.objects.create(
            user=self.user,
            service_list="mc",
            prefer_gender="M",
            status="pending",
            location="seoul",
            wedding_datetime="2024-12-12",
            wedding_hall="테스트 결혼식장",
        )

        # Then: 관련 전문가에게 알림이 생성되어야 함
        notification_exists = Notification.objects.filter(
            receiver=self.expert_user, notification_type="estimation_request"
        ).exists()

        self.assertTrue(notification_exists, "견적 요청이 생성되면 전문가에게 알림이 생성되어야 합니다.")
