from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_redis import get_redis_connection

from chat.models import Message
from notifications.models import Notification

channel_layer = get_channel_layer()
redis_conn = get_redis_connection("default")


@receiver(post_save, sender=Message)
def estimation_post_save_handler(sender, instance, created, **kwargs):
    if created:
        message = instance
        notification = Notification.objects.create(
            receiver=message.sender,
            title=f"""
            {message.sender.name}님이 메시지를 보냈습니다. 확인해보세요!
            """,
            message=message.content,
            notification_type="message",
            is_read=False,
        )
