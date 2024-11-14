from django.db import models

from expert.models import Expert
from users.models import User


class ChatRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    user_exist = models.BooleanField(default=True)
    expert_exist = models.BooleanField(default=True)


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to="images/chat/", null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
