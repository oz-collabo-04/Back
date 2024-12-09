from django.db import models

from common.constants.choices import RESERVATION_STATUS_CHOICES
from estimations.models import Estimation


class Reservation(models.Model):
    estimation = models.OneToOneField(Estimation, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=RESERVATION_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CancelManager(models.Model):
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
