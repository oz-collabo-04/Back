from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.test import TestCase

from estimations.models import Estimation, EstimationsRequest
from expert.models import Expert
from notifications.models import Notification

User = get_user_model()


class EstimationSignalTest(TestCase):
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

        # 견적 요청 생성
        self.estimation_request = EstimationsRequest.objects.create(
            user=self.user,
            service_list="mc",
            prefer_gender="male",
            status="pending",
            location="Seoul",
            wedding_datetime="2024-12-12",
        )

    def test_notification_created_on_estimation_create(self):
        # Given: 전문가가 견적서를 생성합니다.
        estimation = Estimation.objects.create(
            request=self.estimation_request,
            expert=self.expert,
            service="mc",
            location="Seoul",
            due_date="2024-12-20",
            charge=150000,
        )

        # When: post_save 시그널이 트리거됩니다.
        # Then: 수신자를 위한 알림이 생성되어야 합니다.
        notification_exists = Notification.objects.filter(receiver=self.user, notification_type="estimation").exists()

        self.assertTrue(notification_exists, "견적서가 생성되면 알림이 생성되어야 합니다.")
