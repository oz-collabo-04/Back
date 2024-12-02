from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from reviews.models import Review


@receiver(post_save, sender=Review)
def review_post_save_handler(sender, instance, created, **kwargs):
    if created:
        review = instance
        notification = Notification.objects.create(
            receiver=review.reservation.estimation.request.user,
            title=f"""
            {review.reservation.estimation.request.user}님이 리뷰를 남겼습니다. 확인해보세요!
            """,
            message=f"""
            - 내용: {review.content}
            - 평점: {review.rating}
            """,
            notification_type="review",
            is_read=False,
        )
