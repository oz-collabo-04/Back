from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_redis import get_redis_connection

from estimations.models import EstimationsRequest
from expert.models import Expert
from notifications.models import Notification

channel_layer = get_channel_layer()
redis_conn = get_redis_connection("default")


@receiver(post_save, sender=EstimationsRequest)
def estimation_post_save_handler(sender, instance, created, **kwargs):
    if created:
        request = instance
        experts = Expert.objects.filter(
            service__in=request.service_list,
            user__gender=request.prefer_gender,
            location=request.location,
        )
        for expert in experts:
            Notification.objects.create(
                receiver=expert.user.id,
                title=f"""
                {request.user.name}님이 견적 요청을 보냈습니다. 확인해보세요!
                """,
                message=f"""
                - 요청 서비스: {request.get_service_list_display()}
                - 선호 하는 성별: {request.get_prefer_gender_display()}
                - 결혼식 정보:
                    - 결혼식 예상 지역: {request.get_location_display()}
                    - 결혼식장: {request.wedding_hall}
                    - 결혼식 예상 날짜: {request.wedding_datetime}
                """,
                notification_type="estimation_request",
                is_read=False,
            )
