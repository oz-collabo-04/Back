from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification

channel_layer = get_channel_layer()


# Django signal을 사용하여 Notification 객체가 생성될 때 웹소켓으로 알림을 전달
@receiver(post_save, sender=Notification)
def send_notification_signal(sender, instance, created, **kwargs):
    if created:
        group_name = f"notification_{instance.receiver.id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "notification": {
                    "id": instance.id,
                    "title": instance.title,
                    "message": instance.message,
                    "notification_type": instance.notification_type,
                    "is_read": instance.is_read,
                },
            },
        )
