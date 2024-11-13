from django.db import models
from multiselectfield import MultiSelectField

from common.constants.choices import (
    AREA_CHOICES,
    BOOKING_STATUS_CHOICES,
    GENDER_CHOICES,
    SERVICE_CHOICES,
)
from expert.models import Expert
from users.models import User


class Estimation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    service_list = MultiSelectField(choices=SERVICE_CHOICES, max_length=10)
    location = MultiSelectField(choices=AREA_CHOICES, max_length=30, max_choices=3)
    due_date = models.DateField()
    discount = models.PositiveIntegerField(null=True, blank=True)
    total_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EstimationsRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_list = MultiSelectField(choices=SERVICE_CHOICES, max_length=10)
    prefer_gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    location = MultiSelectField(choices=AREA_CHOICES, max_length=30, max_choices=3)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
