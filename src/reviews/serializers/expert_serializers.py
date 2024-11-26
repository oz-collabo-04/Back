from rest_framework import serializers

from reviews.models import Review
from reviews.serializers.guest_seriailzers import (
    ReviewImagesSerializers,
    UserInfoSerializer,
)


class ReviewListSerializer(serializers.ModelSerializer):
    review_images = ReviewImagesSerializers(many=True, read_only=True)
    user = UserInfoSerializer(source="reservation.estimations.request.user", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "user", "reservation", "content", "rating", "review_images", "created_at", "updated_at")
        read_only_fields = (
            "id",
            "user",
            "reservation",
            "content",
            "rating",
            "review_images",
            "created_at",
            "updated_at",
        )
