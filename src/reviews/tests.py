from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from estimations.models import Estimation, EstimationsRequest
from expert.models import Expert
from reservations.models import Reservation
from reviews.models import Review

User = get_user_model()


class ReviewAPITestCase(APITestCase):
    def setUp(self):
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            name="testuser",
            password="password123",
            email="test@example.com",
            gender="M",
            phone_number="010-1234-5678",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

        # Expert 객체 생성
        self.expert = Expert.objects.create(
            user=self.user,
            expert_image="path/to/image.jpg",
            service="snap",
            available_location="seoul",
            standard_charge="100000",
            appeal="Passionate about delivering great snap services",
        )

        # EstimationsRequest 객체 생성
        self.request = EstimationsRequest.objects.create(
            user=self.user,
            service_list=["snap"],  # SERVICE_CHOICES에서 사용 가능한 값으로 수정
            prefer_gender="M",
            location=["seoul"],  # AREA_CHOICES에서 사용 가능한 값으로 수정
            wedding_hall="Sample Wedding Hall",
            wedding_datetime=timezone.now() + timedelta(days=7),
            status="open",
        )

        # Estimation 객체 생성
        self.estimation = Estimation.objects.create(
            expert=self.expert,
            request=self.request,  # EstimationsRequest 객체 연결
            service="snap",
            location="seoul",
            due_date="2024-12-01",
            charge=100000,
        )

        # Reservation 객체 생성
        self.reservation = Reservation.objects.create(
            estimation=self.estimation,
            status="confirmed",
        )

        # 리뷰 객체 생성
        self.review = Review.objects.create(
            reservation=self.reservation,
            content="Initial Review",
            rating=4,
        )

    def test_create_review(self):
        """리뷰 생성 테스트"""
        # 리뷰 데이터
        review_data = {
            "reservation": self.reservation.id,
            "content": "Great service!",
            "rating": 5.0,
        }
        url = reverse("review-list-create")
        response = self.client.post(url, review_data, headers={"Authorization": f"Bearer {self.access}"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], review_data["content"])
        self.assertEqual(response.data["rating"], review_data["rating"])

    def test_list_reviews(self):
        """리뷰 리스트 조회 테스트"""
        url = reverse("review-list-create")

        response = self.client.get(url, headers={"Authorization": f"Bearer {self.access}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_review(self):
        """리뷰 상세 조회 테스트"""
        url = reverse("review-detail", kwargs={"review_id": self.review.id})

        response = self.client.get(url, headers={"Authorization": f"Bearer {self.access}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.review.id)
        self.assertEqual(response.data["rating"], self.review.rating)
        self.assertEqual(response.data["content"], self.review.content)
        self.assertEqual(response.data["user"]["id"], self.review.reservation.estimation.request.user.id)

    def test_update_review(self):
        """리뷰 수정 테스트"""
        updated_data = {"content": "Updated Review", "rating": 3.0}
        url = reverse("review-detail", kwargs={"review_id": self.review.id})

        response = self.client.patch(url, updated_data, headers={"Authorization": f"Bearer {self.access}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], updated_data["content"])
        self.assertEqual(response.data["rating"], updated_data["rating"])

    def test_delete_review(self):
        """리뷰 삭제 테스트"""
        url = reverse("review-detail", kwargs={"review_id": self.review.id})

        response = self.client.delete(url, headers={"Authorization": f"Bearer {self.access}"})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())
