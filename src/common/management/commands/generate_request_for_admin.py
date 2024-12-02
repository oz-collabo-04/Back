import random

from django.core.management import BaseCommand
from django.utils import timezone
from faker import Faker

from estimations.models import Estimation, EstimationsRequest, RequestManager
from expert.models import Expert
from users.models import User


class Command(BaseCommand):
    help = "Generate dummy data for all models with Faker."

    def handle(self, *args, **kwargs):
        faker = Faker("ko_KR")
        admin = User.objects.get(email="admin@example.com")

        guest_users = User.objects.filter(is_expert=False, expert__isnull=True)

        for user in guest_users:
            # Generate Estimation data for each expert
            request = EstimationsRequest.objects.create(
                user=user,
                service_list=[admin.expert.service],
                location=random.choice(admin.expert.available_location),
                wedding_hall=faker.building_name(),
                wedding_datetime=timezone.now() + timezone.timedelta(days=random.randint(6, 14)),
                status="pending",
            )

            RequestManager.objects.create(
                request=request,
                expert=admin.expert,
            )
            print(
                f"""
                Created EstimationsRequest for admin.\n
                request id: {request.id}
                user id: {request.id}
                """
            )
