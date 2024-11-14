from django.db import models
from multiselectfield import MultiSelectField

from common.constants.choices import AREA_CHOICES, SERVICE_CHOICES
from users.models import User


class Expert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="images/experts/profile/")
    available_location = MultiSelectField(choices=AREA_CHOICES, max_length=20)
    appeal = models.TextField(max_length=300)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(null=True, blank=True)


class Career(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    description = models.TextField(max_length=300)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class ExpertImage(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/experts/careers/")


class Service(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    service_name = models.CharField(choices=SERVICE_CHOICES, max_length=10)
    charge = models.PositiveIntegerField()
