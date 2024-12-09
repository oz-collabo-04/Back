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

User = get_user_model()


class ReservationTestCase(APITestCase):
    def setUp(self):
        # 사용자 생성 및 액세스 토큰 발급
        self.user = User.objects.create_user(
            email="test@example.com", name="testuser", gender="M", phone_number="010-1234-1234"
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

        # Create Guest User
        self.guest_users = [
            User.objects.create_user(
                email=f"test{i}@example.com", name=f"testuser{i}", gender="M", phone_number=f"010-123{i}-1234"
            )
            for i in range(1, 3)
        ]
        # Create Expert User
        self.expert_users = [
            User.objects.create_user(
                email=f"test{i}@example.com", name=f"testuser{i}", gender="M", phone_number=f"010-{i}234-1234"
            )
            for i in range(3, 5)
        ]
        self.experts = [
            Expert.objects.create(
                user=user, service="snap", standard_charge=30000, available_location="seoul", appeal="test appeal text"
            )
            for user in self.expert_users
        ]
        # 사용자 권한 설정(expert 사용자)
        self.expert_user = self.expert_users[0]
        self.expert_refresh = RefreshToken.for_user(self.expert_user)
        self.expert_access = str(self.expert_refresh.access_token)
        self.expert_profile = Expert.objects.get(user=self.expert_user)
        self.expert_user.is_expert = True
        self.expert_user.save()
        self.client.force_authenticate(user=self.expert_user)

        # Create EstimationRequest
        self.requests = [
            EstimationsRequest.objects.create(
                user=user,
                service_list="snap",
                location="seoul",
                prefer_gender="M",
                wedding_hall="wedding hall",
                wedding_datetime=timezone.now() + timedelta(days=1),
                status="pending",
            )
            for user in self.guest_users
        ]
        # Estimation 생성
        self.estimations = [
            Estimation.objects.create(
                expert=expert,
                request=request,
                service="snap",
                location="seoul",
                due_date=request.wedding_datetime.date(),
                charge=100000,
            )
            for expert, request in zip(self.experts, self.requests)
        ]

        # 캘린더 테스트를 위한 예약 데이터 생성
        self.calendar_reservations = [
            Reservation.objects.create(
                estimation=estimation,
                status="pending",
            )
            for estimation in self.estimations
        ]

    def test_list_reservations(self):
        # given
        # Reservation 생성 (이미 setUp에서 생성되었으므로 추가 생성 불필요)
        self.assertEqual(Reservation.objects.all().count(), 2)  # 기존 예약 + setUp에서 생성된 예약

        url = reverse("reservation-list")

        # when
        response = self.client.get(url, headers={"Authorization": f"Bearer {self.access}"})

        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Reservation.objects.count())

    def test_create_reservation(self):
        initial_count = Reservation.objects.count()
        estimation = Estimation.objects.create(
            expert=self.experts[0],
            request=self.requests[0],
            service="snap",
            location="seoul",
            due_date=self.requests[0].wedding_datetime.date(),
            charge=100000,
        )

        data = {"estimation_id": estimation.id}
        url = reverse("reservation-create")
        response = self.client.post(url, data=data, headers={"Authorization": f"Bearer {self.access}"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), initial_count + 1)
        self.assertEqual(response.data["estimation"]["id"], data["estimation_id"])

    def test_get_reservation_detail(self):
        estimation = Estimation.objects.create(
            expert=self.experts[0],
            request=self.requests[0],
            service="snap",
            location="seoul",
            due_date=self.requests[0].wedding_datetime.date(),
            charge=100000,
        )
        reservation = Reservation.objects.create(
            estimation_id=estimation.id,
            status="pending",
        )
        url = reverse("reservation-retrieve-update", kwargs={"reservation_id": reservation.id})
        response = self.client.get(url, headers={"Authorization": f"Bearer {self.access}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], reservation.id)
        self.assertEqual(response.data["status"], reservation.status)

    def test_update_reservation(self):
        estimation = Estimation.objects.create(
            expert=self.experts[0],
            request=self.requests[0],
            service="snap",
            location="seoul",
            due_date=self.requests[0].wedding_datetime.date(),
            charge=100000,
        )
        reservation = Reservation.objects.create(
            estimation_id=estimation.id,
            status="pending",
        )
        data = {"status": "completed"}
        url = reverse("reservation-retrieve-update", kwargs={"reservation_id": reservation.id})

        response = self.client.patch(url, data=data, headers={"Authorization": f"Bearer {self.access}"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], data["status"])

    def test_expert_reservation_list(self):
        """Expert의 예약 리스트 조회"""
        url = reverse("expert-reservation-list")
        response = self.client.get(url, headers={"Authorization": f"Bearer {self.expert_access}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expert_reservation_detail(self):
        """Expert의 예약 상세 조회 테스트"""
        url = reverse("expert-reservation-detail", kwargs={"reservation_id": self.calendar_reservations[0].id})
        response = self.client.get(url, headers={"Authorization": f"Bearer {self.expert_access}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.calendar_reservations[0].id)
        self.assertEqual(response.data["status"], "pending")

    def test_reservation_list_for_calendar(self):
        """캘린더 API 조회 테스트"""
        year = timezone.now().year
        month = timezone.now().month

        url = f"{reverse('reservation-list-for-calendar')}?year={year}&month={month}"

        response = self.client.get(url, headers={"Authorization": f"Bearer {self.expert_access}"})

        # 디버깅용 추가 정보
        print(f"User: {self.expert_user}")
        print(f"Is Authenticated: {self.expert_user.is_authenticated}")
        print(f"Has Expert Profile: {hasattr(self.expert_user, 'expert')}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Content: {response.content}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 데이터가 있는지 확인
        self.assertGreater(len(response.data), 0)

        for reservation in response.data:
            self.assertEqual(reservation.get("service_display"), "스냅 촬영")
            self.assertEqual(reservation.get("location_display"), "서울특별시")
