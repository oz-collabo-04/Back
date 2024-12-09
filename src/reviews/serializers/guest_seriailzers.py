from django.db import transaction
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
        fields = ("id", "review", "image")
        read_only_fields = ["id", "review"]


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImagesSerializers(many=True, required=False)
    user = UserInfoSerializer(source="reservation.estimation.request.user", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "user", "reservation", "content", "rating", "images", "created_at", "updated_at")
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        images = validated_data.pop("images", [])

        with transaction.atomic():
            review = Review.objects.create(**validated_data)
            if images:
                image_serializer = ReviewImagesSerializers(data=[{"image": image} for image in images], many=True)
                image_serializer.is_valid(raise_exception=True)
                image_serializer.save(review=review)

        return review

    def update(self, instance, validated_data):
        images = validated_data.pop("images", [])

        with transaction.atomic():
            # 새로운 리뷰 이미지가 있으면
            if images:
                # 기존의 리뷰 이미지 삭제
                ReviewImages.objects.filter(review=instance).delete()

                # 새로운 리뷰 이미지 저장
                image_serializer = ReviewImagesSerializers(data=[{"image": image} for image in images], many=True)
                image_serializer.is_valid(raise_exception=True)
                image_serializer.save(review=instance)

            # 기존 인스턴스 필드를 업데이트
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            # 변경된 내용을 저장
            instance.save()

            return instance
