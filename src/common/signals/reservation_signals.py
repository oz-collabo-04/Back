from django.db.models.signals import post_save
from django.dispatch import receiver
from django_redis import get_redis_connection
from notifications.models import Notification
from channels.layers import get_channel_layer

from reservations.models import Reservation

channel_layer = get_channel_layer()
redis_conn = get_redis_connection("default")


@receiver(post_save, sender=Reservation)
def estimation_post_save_handler(sender, instance, created, **kwargs):
    if created:
        reservation = instance
        notification = Notification.objects.create(
            receiver=reservation.estimation.request.user,
            title=f"""
            {reservation.estimation.request.user.name}님이 예약하셨습니다. 확인해보세요!
            """,
            message=f"""
            - 진행 서비스: {reservation.estimation.service}
            
            - 진행 지역: {reservation.estimation.location}
            
            - 진행 날짜: {reservation.estimation.due_date}
            
            - 견적 금액: {reservation.estimation.charge}
            """,
            notification_type='reserved',
            is_read=False
        )