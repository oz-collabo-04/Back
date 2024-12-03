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

        # 1. admin 생성
        admin = self.create_superuser(fake)

        # 2. admin의 견적 요청 데이터 생성
        request = self.create_request_by_admin(fake, admin)

        # 3. admin의 견적 요청에 해당하는 전문가 데이터 생성
        self.create_expert_for_admin_request(fake, request)

        # 4. 위에서 생성한 EstimationRequest와 사용하여 RequestManager 데이터 생성
        self.create_request_manager_for_admin(request)

        # 4. Estimation 데이터 생성
        self.create_estimations_for_admin(request)

        # 5. Reservation 및 CancelManager 생성
        self.create_reservations_for_admin(fake, request)

        # 6. Review 데이터 생성
        self.create_reviews_by_admin(fake, request)

        # 7. Notification 데이터 생성
        self.create_notifications_for_admin(fake, admin)

        print("All data for admin generated successfully.")

    def create_superuser(self, fake):
        print("Creating superuser and Expert profile...")
        if not User.objects.filter(email="admin@example.com").exists():
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
                is_expert=True,
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

            return superuser
        return User.objects.filter(email="admin@example.com").first()

    def create_request_by_admin(self, fake, admin):
        print("Creating Estimation Requests...")
        service_list = [service[0] for service in SERVICE_CHOICES]

        request = EstimationsRequest.objects.create(
            user=admin,
            service_list=random.sample(service_list, random.randint(1, 4)),
            prefer_gender=random.choice(GENDER_CHOICES)[0],
            location=random.choice(AREA_CHOICES)[0],
            wedding_hall=fake.building_name() + "wedding_hole",
            wedding_datetime=timezone.now() + timedelta(days=random.randint(1, 30)),
            status="pending",
        )

        print(
            f"""
            Admin EstimationRequest Created.\n
            request id: {request.id}
            request service_list: {request.service_list}
            request prefer_gender: {request.prefer_gender}
            request location: {request.location} 
            """
        )

        return request

    def create_expert_for_admin_request(self, fake, request):
        print("Creating Expert & Career for Admin EstimationRequest...")

        users = [
            User.objects.create_user(
                email=f"{fake.first_name() + str(random.randint(1, 999))}@naver.com",
                name=fake.name(),
                phone_number=f"010-{random.randint(1111, 9999)}-{random.randint(1111, 9999)}",
                gender=request.prefer_gender,
                profile_image=fake.image_url(width=200, height=200),
                is_active=True,
                is_expert=True,
            )
            for _ in range(1, 10)
        ]

        experts = [
            Expert.objects.create(
                user=user,
                expert_image=fake.image_url(width=200, height=200),
                service=random.choice(request.service_list),
                standard_charge=random.randint(100000, 900000),
                available_location=request.location,
                appeal=fake.paragraph(nb_sentences=5),
            )
            for user in users
        ]

        for expert in experts:
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
                {"".join([f"{career}\n" for index, career in enumerate(careers)])}
                """
            )

    def create_request_manager_for_admin(self, request):
        experts = Expert.objects.filter(
            service__in=request.service_list,
            user__gender=request.prefer_gender,
            available_location__contains=request.location,
        )

        if experts.exists():
            print(f"Creating RequestManager Object for Experts providing the service item: {request.service_list}")
            for expert in experts:
                # 전문가 각각에 요청 관리를 위한 모델을 생성
                manager = RequestManager.objects.create(
                    request=request,
                    expert=expert,
                )
                print(
                    f"""
                    RequestManager Created.\n
                    RequestManager id: {manager.id}
                    RequestManager email: {manager.request.user.email}
                    Expert Email: {expert.user.email}
                    """
                )

    def create_estimations_for_admin(self, request):
        managers = RequestManager.objects.filter(request=request)
        if managers:
            print("Creating Estimations...")
            for manager in managers:
                estimation = Estimation.objects.create(
                    request=manager.request,
                    expert=manager.expert,
                    service=manager.expert.service,
                    location=manager.request.location,
                    due_date=manager.request.wedding_datetime,
                    charge=random.randint(10000, 500000),
                )
                print(
                    f"""
                    Created Estimation for admin - {manager.request.user.email}.\n
                    Estimation id: {estimation.id}
                    request id: {manager.request.id}
                    Expert id: {manager.expert.id} 
                    """
                )

    def create_reservations_for_admin(self, fake, request):
        estimations = Estimation.objects.filter(request=request)
        if estimations.exists():
            print("Creating Reservations...")

            # 모든 견적을 for문으로 순회하며 예약객체를 생성
            for estimation in estimations:
                reservation = Reservation.objects.create(
                    estimation=estimation,
                    status=random.choice(RESERVATION_STATUS_CHOICES)[0],
                )
                print(
                    f"""
                    Created Reservation: {reservation.id}
                    """
                )
                # 생성된 예약이 취소된 상태이면 취소 사유 객체를 생성
                if reservation.status in ["cancelled", "cancel"]:
                    CancelManager.objects.create(reservation=reservation, reason=fake.paragraph(nb_sentences=3))
                    print(
                        f"""
                        Created RequestManager Object for Reservation_id:{reservation.id}
                        """
                    )

    def create_reviews_by_admin(self, fake, request):
        # 이용 완료된 예약객체를 모두 가져옴
        reservations = Reservation.objects.filter(estimation__request=request, status="completed")
        if reservations.exists():
            print("Creating Reviews...")

            if reservations.exists():
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
                    print(
                        f"""
                        Created Review.\n
                        review_id: {review.id}
                        review_user_email: {review.reservation.estimation.request.user.email}
                        """
                    )

    def create_notifications_for_admin(self, fake, admin):
        print("Creating Notifications...")

        # 랜덤한 알림을 1 ~ 5개 생성
        for _ in range(1, random.randint(1, 5)):
            notification = Notification.objects.create(
                receiver=admin,
                title=fake.paragraph(nb_sentences=1),
                message=fake.paragraph(nb_sentences=2),
                notification_type=random.choice(NOTIFICATION_TYPE_CHOICES)[0],
                is_read=False,
            )
            print(
                f"""
                Created Notification.\n
                receiver_id: {admin.id}\n
                notification_type: {notification.notification_type}\n
                title: {notification.title}\n
                """
            )
