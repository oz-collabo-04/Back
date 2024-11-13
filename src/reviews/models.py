from django.db import models

from common.constants.choices import SCORE_CHOICES
from reservations.models import Reservation


class Review(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReviewImages(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/reviews/")


class Rating(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    score = models.DecimalField(choices=SCORE_CHOICES, max_digits=2, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
