from django.contrib.auth import get_user_model
from django.db import models

from common.constants.choices import NOTIFICATION_TYPE_CHOICES

User = get_user_model()


class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
