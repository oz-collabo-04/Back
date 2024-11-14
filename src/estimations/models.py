from django.db import models
from multiselectfield import MultiSelectField

from common.constants.choices import (
    AREA_CHOICES,
    GENDER_CHOICES,
    REQUEST_STATUS_CHOICES,
    SERVICE_CHOICES,
)
from expert.models import Expert
from users.models import User


class EstimationsRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_list = MultiSelectField(choices=SERVICE_CHOICES, max_length=10)
    prefer_gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    location = MultiSelectField(choices=AREA_CHOICES, max_length=30, max_choices=3)
    wedding_hall = models.CharField(max_length=50)
    wedding_datetime = models.DateTimeField()
    status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Estimation(models.Model):
    request = models.ForeignKey(EstimationsRequest, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    service = models.CharField(choices=SERVICE_CHOICES, max_length=10)
    location = models.CharField(choices=AREA_CHOICES, max_length=30)
    due_date = models.DateField()
    charge = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RequestManager(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, related_name="received_requests")
    request = models.ForeignKey(EstimationsRequest, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
