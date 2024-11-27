from rest_framework import serializers

from common.constants.choices import SERVICE_CHOICES
from estimations.models import Estimation, EstimationsRequest, RequestManager
from users.models import User


# 유저의 요청에 대한 전문가의 견적 등록 요청
class EstimationCreateByExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estimation
        fields = ["id", "request", "expert", "due_date", "service", "charge", "created_at", "updated_at"]
        read_only_fields = ("id", "expert", "created_at", "updated_at")


# 유저의 요청에 대한 전문가의 견적 수정 요청
class EstimationUpdateByExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estimation
        fields = ["id", "request", "expert", "due_date", "service", "charge", "created_at", "updated_at"]
        read_only_fields = ("id", "request", "expert", "created_at", "updated_at")


class RequestUserSerializerForExpert(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "phone_number", "name"]


class EstimationRequestSerializerForExpert(serializers.ModelSerializer):
    user = RequestUserSerializerForExpert(read_only=True)
    service_list = serializers.MultipleChoiceField(choices=SERVICE_CHOICES, read_only=True)

    class Meta:
        model = EstimationsRequest
        fields = "__all__"


class EstimationRequestListForExpertSerializer(serializers.ModelSerializer):
    request = EstimationRequestSerializerForExpert(read_only=True)

    class Meta:
        model = RequestManager
        fields = ["id", "expert", "request", "created_at", "updated_at"]
        read_only_fields = ("id", "expert", "request", "created_at", "updated_at")
