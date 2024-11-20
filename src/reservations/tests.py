from datetime import timedelta

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from expert.models import Expert
from reservations.models import Reservation
from estimations.models import Estimation, EstimationsRequest

User = get_user_model()


class ReservationTestCase(APITestCase):
    def setUp(self):
        # 사용자 생성 및 액세스 토큰 발급
        self.user = User.objects.create_user(
            email="test@example.com",
            name="testuser",
            gender="M",
            phone_number="010-1234-1234"
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

        # Create Guest User
        self.guest_users = [
            User.objects.create_user(
                email=f"test{i}@example.com",
                name=f"testuser{i}",
                gender="M",
                phone_number=f"010-123{i}-1234"
            ) for i in range(1, 2)
        ]
        # Create Expert User
        self.expert_users = [
            User.objects.create_user(
                email=f"test{i}@example.com",
                name=f"testuser{i}",
                gender="M",
                phone_number=f"010-{i}234-1234"
            ) for i in range(3, 4)
        ]
        self.experts = [
            Expert.objects.create(
                user=user,
                service='snap',
                standard_charge=30000,
                available_location='seoul',
                appeal='test appeal text'
            ) for user in self.expert_users
        ]
        # Create EstimationRequest
        self.requests = [
            EstimationsRequest.objects.create(
                user=user,
                service_list='snap',
                location='seoul',
                prefer_gender='M',
                wedding_hall='wedding hall',
                wedding_datetime=timezone.now() + timedelta(days=1),
                status='pending'
            ) for user in self.guest_users
        ]
        # Estimation 생성
        self.estimations = [Estimation.objects.create(
            expert=expert,
            request=request,
            service="snap",
            location="seoul",
            due_date=timezone.now().date(),
            charge=100000,
        ) for expert, request in zip(self.experts, self.requests)]

    def test_list_reservations(self):
        # given
        # Reservation 생성
        for estimation in self.estimations:
            Reservation.objects.create(
                estimation=estimation,
                status="pending",
            )
        self.assertEqual(Reservation.objects.all().count(), len(self.estimations))

        url = reverse('reservation-list')

        # when
        response = self.client.get(url, headers={'Authorization': f'Bearer {self.access}'})

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Reservation.objects.count())

    def test_create_reservation(self):
        data = {"estimation_id": self.estimations[0].id}
        url = reverse('reservation-create')
        response = self.client.post(url, data=data, headers={'Authorization': f'Bearer {self.access}'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.all().count(), 1)
        self.assertEqual(response.data["estimation"]["id"], data["estimation_id"])

    def test_get_reservation_detail(self):
        reservation = Reservation.objects.create(
            estimation_id=self.estimations[0].id,
            status="pending",
        )
        url = reverse('reservation-retrieve-update', kwargs={'reservation_id': reservation.id})
        response = self.client.get(url, headers={'Authorization': f'Bearer {self.access}'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], reservation.id)
        self.assertEqual(response.data["status"], reservation.status)

    def test_update_reservation(self):
        reservation = Reservation.objects.create(
            estimation_id=self.estimations[0].id,
            status="pending",
        )
        data = {"status": "completed"}
        url = reverse('reservation-retrieve-update', kwargs={'reservation_id': reservation.id})

        response = self.client.patch(url, data=data, headers={'Authorization': f'Bearer {self.access}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], data["status"])