from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_redis import get_redis_connection

from estimations.models import Estimation
from notifications.models import Notification

channel_layer = get_channel_layer()
redis_conn = get_redis_connection("default")


@receiver(post_save, sender=Estimation)
def estimation_post_save_handler(sender, instance, created, **kwargs):
    if created:
        estimation = instance
        notification = Notification.objects.create(
            receiver=estimation.request.user,
            title=f"""
            {estimation.expert.user.name}님이 견적서를 보냈습니다. 확인해보세요!
            """,
            message=f"""
            - 전문가 정보:
                - 이름: {estimation.expert.user.name}
                - 성별: {estimation.expert.user.gender}
                - 서비스: {estimation.service}
            
            - 진행 예상 지역: {estimation.location}
            
            - 진행 예상 날짜: {estimation.due_date}
            
            - 견적 예상 금액: {estimation.charge}
            """,
            notification_type="estimation",
            is_read=False,
        )
