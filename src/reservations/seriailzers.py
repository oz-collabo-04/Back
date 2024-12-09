from rest_framework import serializers

from common.exceptions import BadRequestException
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
            "request",
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
    chatroom_id = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ("id", "status", "estimation", "chatroom_id", "created_at", "updated_at")
        read_only_fields = ("id", "estimation", "chatroom_id", "created_at", "updated_at")

    def get_chatroom_id(self, obj):
        if not hasattr(obj.estimation, "chatroom"):
            return None
        return obj.estimation.chatroom.id


class ReservationCreateSerializer(serializers.ModelSerializer):
    estimation = EstimationInfoSerializer(read_only=True)
    estimation_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "status", "estimation", "estimation_id", "created_at", "updated_at")
        read_only_fields = ("id", "status", "estimation", "created_at", "updated_at")

    def create(self, validated_data):
        if Reservation.objects.filter(**validated_data, status__in=["confirmed", "completed"]):
            raise BadRequestException("Reservation already exists")
        return Reservation.objects.create(**validated_data, status="confirmed")


class ExpertReservationInfoSerializer(serializers.ModelSerializer):
    estimation = EstimationInfoSerializer(read_only=True)
    guest_info = serializers.SerializerMethodField()
    chatroom_id = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = ("id", "status", "estimation", "guest_info", "chatroom_id", "created_at", "updated_at")
        read_only_fields = ("id", "estimation", "chatroom_id", "created_at", "updated_at")

    def get_guest_info(self, obj):
        # estimation을 통해 요청한 게스트 정보 반환
        if obj.estimation and obj.estimation.request and obj.estimation.request.user:
            user = obj.estimation.request.user
            return {"id": user.id, "name": user.name, "email": user.email, "phone_number": user.phone_number}
        return None

    def get_chatroom_id(self, obj):
        if not hasattr(obj.estimation, "chatroom"):
            return None
        return obj.estimation.chatroom.id


class ReservationListForCalendarSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(source="estimation.request.user", read_only=True)
    service = serializers.CharField(source="estimation.service", read_only=True)
    service_display = serializers.CharField(source="estimation.get_service_display", read_only=True)
    location = serializers.CharField(source="estimation.request.location", read_only=True)
    location_display = serializers.CharField(source="estimation.request.get_location_display", read_only=True)
    wedding_hall = serializers.CharField(source="estimation.request.wedding_hall", read_only=True)
    wedding_datetime = serializers.CharField(source="estimation.request.wedding_datetime", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "user",
            "service",
            "service_display",
            "location",
            "location_display",
            "wedding_hall",
            "wedding_datetime",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
