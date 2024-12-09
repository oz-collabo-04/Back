from django.db import models

from common.constants.choices import RATING_CHOICES
from reservations.models import Reservation


class Review(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    rating = models.DecimalField(choices=RATING_CHOICES, decimal_places=1, max_digits=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReviewImages(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="images/reviews/", null=True, blank=True)
