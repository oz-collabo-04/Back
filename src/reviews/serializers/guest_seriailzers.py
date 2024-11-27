from rest_framework import serializers

from reviews.models import Review, ReviewImages
from users.models import User


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "profile_image"]
        read_only_fields = ["id", "email", "name", "profile_image"]


class ReviewImagesSerializers(serializers.ModelSerializer):

    class Meta:
        model = ReviewImages
        fields = ("id", "image")


class ReviewSerializer(serializers.ModelSerializer):
    review_images = ReviewImagesSerializers(many=True, required=False)
    user = UserInfoSerializer(source="reservation.estimation.request.user", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "user", "reservation", "content", "rating", "review_images", "created_at", "updated_at")
        read_only_fields = ("id", "user", "created_at", "updated_at")
