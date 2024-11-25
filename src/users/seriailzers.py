from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "gender", "phone_number", "profile_image", "prefer_service", "prefer_location"]
        read_only_fields = ("id", "email")


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "profile_image", "is_expert"]
        read_only_fields = ("id", "email")
