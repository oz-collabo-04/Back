from django.db.models.signals import post_save
from django.dispatch import receiver

from chat.models import Message
from notifications.models import Notification


@receiver(post_save, sender=Message)
def chat_post_save_handler(sender, instance, created, **kwargs):
    if created:
        message = instance
        if instance.is_read:
            return

        # 수신자를 설정: 전문가가 보낸 경우 일반 사용자, 사용자가 보낸 경우 전문가
        if message.sender == message.room.user:
            receiver = message.room.expert.user
        else:
            receiver = message.room.user

        # Notification 객체 생성
        notification = Notification.objects.create(
            receiver=receiver,
            title=f"{message.sender.name}님이 메시지를 보냈습니다. 확인해보세요!",
            message=message.content,
            notification_type="message",
            is_read=False,
        )
