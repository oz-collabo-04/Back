from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.test import TestCase

from estimations.models import Estimation, EstimationsRequest
from expert.models import Expert
from notifications.models import Notification
from reservations.models import Reservation
from reviews.models import Review

User = get_user_model()


class ReviewSignalTest(TestCase):
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
            service="mc",
            available_location="seoul",
        )

        # 견적 요청 생성
        self.estimation_request = EstimationsRequest.objects.create(
            user=self.user,
            service_list="mc",
            prefer_gender="M",
            status="pending",
            location="seoul",
            wedding_datetime="2024-12-12",
        )

        # 견적 생성
        self.estimation = Estimation.objects.create(
            request=self.estimation_request,
            expert=self.expert,
            service="mc",
            location="seoul",
            due_date="2024-12-20",
            charge=150000,
        )

        # 예약 생성
        self.reservation = Reservation.objects.create(
            estimation=self.estimation,
            status="confirmed",
        )

    def test_notification_created_on_review_create(self):
        # Given: 리뷰 생성
        review = Review.objects.create(reservation=self.reservation, content="좋은 서비스였습니다!", rating=5)

        # Then: 리뷰를 생성하면 알림이 생성되어야 함
        notification_exists = Notification.objects.filter(
            receiver=self.expert_user, notification_type="review"
        ).exists()

        self.assertTrue(notification_exists, "리뷰가 생성되면 사용자에게 알림이 생성되어야 합니다.")
