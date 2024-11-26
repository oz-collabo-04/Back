from rest_framework import serializers

from estimations.models import Estimation
from expert.models import Expert
from reservations.models import Reservation
from users.models import User


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


class ExpertReservationInfoSerializer(serializers.ModelSerializer):
    estimation = EstimationInfoSerializer(read_only=True)
    guest_info = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ("id", "status", "estimation", "guest_info", "created_at", "updated_at")
        read_only_fields = ("id", "estimation", "created_at", "updated_at")

    def get_guest_info(self, obj):
        # estimation을 통해 요청한 게스트 정보 반환
        if obj.estimation and obj.estimation.request and obj.estimation.request.user:
            user = obj.estimation.request.user
            return {"id": user.id, "name": user.name, "email": user.email, "phone_number": user.phone_number}
        return None
