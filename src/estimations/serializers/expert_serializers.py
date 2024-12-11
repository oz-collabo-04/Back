from rest_framework import serializers

from estimations.models import Estimation, EstimationsRequest, RequestManager
from users.models import User


# 유저의 요청에 대한 전문가의 견적 등록 요청
class EstimationCreateByExpertSerializer(serializers.ModelSerializer):
    service_display = serializers.CharField(source="get_service_display", read_only=True)

    class Meta:
        model = Estimation
        fields = [
            "id",
            "request",
            "expert",
            "due_date",
            "service",
            "service_display",
            "description",
            "charge",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "expert", "service_display", "created_at", "updated_at")


# 유저의 요청에 대한 전문가의 견적 수정 요청
class EstimationUpdateByExpertSerializer(serializers.ModelSerializer):
    service_display = serializers.CharField(source="get_service_display", read_only=True)

    class Meta:
        model = Estimation
        fields = [
            "id",
            "request",
            "expert",
            "due_date",
            "service",
            "service_display",
            "description",
            "charge",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "request", "expert", "service_display", "created_at", "updated_at")


class RequestUserSerializerForExpert(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "phone_number", "name", "profile_image"]


class EstimationRequestSerializerForExpert(serializers.ModelSerializer):
    user = RequestUserSerializerForExpert(read_only=True)
    service_list_display = serializers.CharField(source="get_service_list_display", read_only=True)
    location_display = serializers.CharField(source="get_location_display", read_only=True)
    prefer_gender_display = serializers.CharField(source="get_prefer_gender_display", read_only=True)

    class Meta:
        model = EstimationsRequest
        fields = "__all__"


class EstimationRequestListForExpertSerializer(serializers.ModelSerializer):
    request = EstimationRequestSerializerForExpert(read_only=True)

    class Meta:
        model = RequestManager
        fields = ["id", "expert", "request", "created_at", "updated_at"]
        read_only_fields = ("id", "expert", "request", "created_at", "updated_at")


class EstimationListForExpertSerializer(serializers.ModelSerializer):
    request = EstimationRequestSerializerForExpert(read_only=True)
    service_display = serializers.CharField(source="get_service_display", read_only=True)
    location_display = serializers.CharField(source="get_location_display", read_only=True)

    class Meta:
        model = Estimation
        fields = "__all__"
        read_only_fields = [
            "request",
            "expert",
            "service",
            "service_display",
            "location",
            "location_display",
            "due_date",
            "description",
            "charge",
            "created_at",
            "updated_at",
        ]
