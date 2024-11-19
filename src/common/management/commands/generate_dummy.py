import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from common.constants.choices import (
    AREA_CHOICES,
    GENDER_CHOICES,
    NOTIFICATION_TYPE_CHOICES,
    RATING_CHOICES,
    RESERVATION_STATUS_CHOICES,
    SERVICE_CHOICES,
)
from estimations.models import Estimation, EstimationsRequest, RequestManager
from expert.models import Career, Expert
from notifications.models import Notification
from reservations.models import CancelManager, Reservation
from reviews.models import Review, ReviewImages
from users.models import User


class Command(BaseCommand):
    help = "Generate dummy data for all models with Faker."

    def handle(self, *args, **kwargs):
        fake = Faker("ko_KR")

        # 1. Expert User 데이터 생성
        self.create_expert_users(fake)

        # 2. Guest User 데이터 생성
        self.create_guest_users(fake)

        # 3. EstimationRequest 데이터 생성
        self.create_estimation_requests(fake)

        # 4. Estimation 데이터 생성
        self.create_estimations()

        # 5. Reservation 및 CancelManager 생성
        self.create_reservations(fake)

        # 6.새로운 Booking 데이터 생성
        self.create_reviews(fake)

        # 7. 슈퍼유저 생성
        self.create_superuser(fake)

        print("All data generated successfully.")

    def create_superuser(self, fake):
        print("Creating superuser and Expert profile...")

        superuser = User.objects.create_user(
            email="admin@example.com",
            password="admin1234",
            name=fake.name(),
            phone_number=f"010-{random.randint(1111, 9999)}-{random.randint(1111, 9999)}",
            gender=random.choice(GENDER_CHOICES)[0],
            profile_image=fake.image_url(width=200, height=200),
            is_superuser=True,
            is_active=True,
            is_staff=True,
        )

        Expert.objects.create(
            user=superuser,
            expert_image=fake.image_url(width=200, height=200),
            service=random.choice(SERVICE_CHOICES)[0],
            standard_charge=random.randint(100000, 900000),
            available_location=random.choice(AREA_CHOICES)[0],
            appeal=fake.paragraph(nb_sentences=5),
        )
        print(f"Superuser created: {superuser.email}")
        print(f"Expert profile created for superuser.")

    def create_expert_users(self, fake):
        print("Creating Expert profiles...")
        for i in range(1, 20):
            expert_user = User.objects.create_user(
                email=f"{fake.first_name() + str(random.randint(1, 999))}@naver.com",
                name=fake.name(),
                phone_number=f"010-{random.randint(1111, 9999)}-{random.randint(1111, 9999)}",
                gender=random.choice(GENDER_CHOICES)[0],
                profile_image=fake.image_url(width=200, height=200),
                is_active=True,
            )

            expert = Expert.objects.create(
                user=expert_user,
                expert_image=fake.image_url(width=200, height=200),
                service=random.choice(SERVICE_CHOICES)[0],
                standard_charge=random.randint(100000, 900000),
                available_location=random.choice(AREA_CHOICES)[0],
                appeal=fake.paragraph(nb_sentences=5),
            )

            for _ in range(random.randint(1, 3)):
                random_num = random.randint(1, 5)
                Career.objects.create(
                    expert=expert,
                    title=f"{fake.company()} {random_num}년 근무",
                    description=fake.paragraph(nb_sentences=2),
                    start_date=timezone.now(),
                    end_date=timezone.now().replace(year=timezone.now().year + random_num),
                )
            careers = expert.career_set.all().values_list("title", flat=True)

            # 최종적으로 생성된 전문가의 정보를 출력
            print(
                f"""
                Expert profile created for superuser: \n
                - email: {expert.user.email}\n
                - service: {expert.service}\n
                - charge: {expert.standard_charge}\n
                - location: {expert.get_available_location_display()}\n
                - careers:
                """
            )
            for index, career_title in enumerate(careers):
                print(f"{index}. {career_title}")

    def create_guest_users(self, fake):
        print("Creating Guest Users...")

        for i in range(1, 20):
            guest_user = User.objects.create_user(
                email=f"{fake.first_name() + str(random.randint(1, 999))}@naver.com",
                name=fake.name(),
                phone_number=f"010-{random.randint(1111, 9999)}-{random.randint(1111, 9999)}",
                gender=random.choice(GENDER_CHOICES)[0],
                profile_image=fake.image_url(width=200, height=200),
                is_active=True,
            )

            print(f"Guest User created: {guest_user.email}")

    def create_estimation_requests(self, fake):
        print("Creating Estimation Requests...")
        guest_users = User.objects.filter(expert__isnull=True)
        service_list = [service[0] for service in SERVICE_CHOICES]

        for guest_user in guest_users:
            request = EstimationsRequest.objects.create(
                user=guest_user,
                service_list=random.sample(service_list, random.randint(1, 4)),
                prefer_gender=random.choice(GENDER_CHOICES)[0],
                location=random.choice(AREA_CHOICES)[0],
                wedding_hall=fake.building_name() + "wedding_hole",
                wedding_datetime=timezone.now() + timedelta(days=random.randint(1, 30)),
                status="pending",
            )

            # 요청 서비스를 제공하는 전문가를 가져옴
            experts = Expert.objects.filter(service__in=request.service_list)

            print(f"Creating RequestManager Object for Experts providing the service item: {request.service_list}")
            for expert in experts:
                # 위에서 가져온 전문가 각각에 요청 관리를 위한 모델을 생성
                manager = RequestManager.objects.create(
                    request=request,
                    expert=expert,
                )
                print(
                    f"""
                    RequestManager Created.
                    RequestManager id: {manager.id}\n
                    Expert Email: {expert.user.email}
                    """
                )

    def create_estimations(self):
        print("Creating Estimations...")
        expert_users = User.objects.filter(expert__isnull=False)
        requests = EstimationsRequest.objects.filter(status="pending")

        for request in requests:
            for user in expert_users:
                estimation = Estimation.objects.create(
                    request=request,
                    expert=user.expert,
                    service=random.choice(request.service_list),
                    location=random.choice(AREA_CHOICES)[0],
                    due_date=request.wedding_datetime,
                    charge=random.randint(10000, 50000),
                )
                print(
                    f"""
                    Created Estimation for request user - {request.user.email}.\n
                    Estimation id: {estimation.id}\n
                    request id: {request.id}\n
                    Expert id: {user.expert.id}\n 
                """
                )

    def create_reservations(self, fake):
        print("Creating Reservations...")
        estimations = Estimation.objects.filter(request__status="pending")

        # 모든 견적을 for문으로 순회하며 예약객체를 생성
        for estimation in estimations:
            reservation = Reservation.objects.create(
                estimation=estimation,
                status=random.choice(RESERVATION_STATUS_CHOICES)[0],
            )
            print(f"Created Reservation: {reservation.id}")
            # 생성된 예약이 취소된 상태이면 취소 사유 객체를 생성
            if reservation.status in ["cancelled", "cancel"]:
                CancelManager.objects.create(reservation=reservation, reason=fake.paragraph(nb_sentences=3))
                print(f"Created RequestManager Object for Reservation_id:{reservation.id}")

    def create_reviews(self, fake):
        print("Creating Reviews...")
        # 이용 완료된 예약객체를 모두 가져옴
        reservations = Reservation.objects.filter(status="completed")

        # for문으로 이용완료된 Reservation의 쿼리셋을 모두 순회하며 Review를 생성
        for reservation in reservations:
            review = Review.objects.create(
                reservation=reservation,
                content=fake.paragraph(nb_sentences=3),
                rating=random.choice(RATING_CHOICES)[0],
            )
            for i in range(1, 3):
                ReviewImages.objects.create(
                    review=review,
                    image=fake.image_url(width=200, height=200),
                )
            print(f"Created Review: {review.id}")

    def create_notifications(self, fake):
        print("Creating Notifications...")
        users = User.objects.filter(is_active=True)

        # 모든 유저를 대상으로 랜덤한 알림을 1 ~ 5개 생성
        for user in users:
            for _ in range(1, random.randint(1, 5)):
                notification = Notification.objects.create(
                    receiver=user,
                    title=fake.sentence(),
                    message=fake.paragraph(nb_sentences=3),
                    notification_type=random.choice(NOTIFICATION_TYPE_CHOICES)[0],
                    is_read=False,
                )
                print(
                    f"""
                    Created Notification.\n
                    receiver_id: {user.id}\n
                    notification_type: {notification.notification_type}\n
                    title: {notification.title}\n
                """
                )
