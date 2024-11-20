from rest_framework import serializers

from estimations.models import Estimation
from expert.models import Expert
from reservations.models import Reservation
from users.models import User  # 사용자 모델 위치 확인 필요


class UserInfoSerializer(serializers.ModelSerializer):  # 사용자 정보를 직렬화
    class Meta:
        model = User
        fields = ("id", "name", "email", "phone_number")


class ExpertInfoSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Expert
        fields = ("id", "user", "expert_image")


class EstimationInfoSerializer(serializers.ModelSerializer):
    request_user = UserInfoSerializer(source="request.user", read_only=True)
    expert = ExpertInfoSerializer(read_only=True)

    class Meta:
        model = Estimation
        fields = (
            "id",
            "request_id",
            "request_user",
            "expert",
            "service",
            "location",
            "due_date",
            "charge",
            "created_at",
        )


class ReservationInfoSerializer(serializers.ModelSerializer):
    estimation = EstimationInfoSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "status", "estimation", "created_at", "updated_at")
        read_only_fields = ("id", "estimation", "created_at", "updated_at")


class ReservationCreateSerializer(serializers.ModelSerializer):
    estimation = EstimationInfoSerializer(read_only=True)
    estimation_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "status", "estimation", "estimation_id", "created_at", "updated_at")
        read_only_fields = ("id", "status", "estimation", "created_at", "updated_at")
