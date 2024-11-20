from datetime import datetime, timedelta

from rest_framework import fields, serializers

from common.constants.choices import SERVICE_CHOICES
from estimations.models import Estimation, EstimationsRequest
from expert.seriailzers import ExpertDetailSerializer


class EstimationsRequestSerializer(serializers.ModelSerializer):
    service_list = fields.MultipleChoiceField(choices=SERVICE_CHOICES)

    class Meta:
        model = EstimationsRequest
        fields = [
            "id",
            "user",
            "service_list",
            "prefer_gender",
            "wedding_hall",
            "wedding_datetime",
            "location",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "status", "created_at", "updated_at"]

    def validate_wedding_datetime(self, value):
        today = datetime.now().date() + timedelta(days=3)
        if value < today:
            raise serializers.ValidationError("결혼식 진행 예정일은 오늘로부터 3일 이후여야 합니다.")
        return value


# 견적 리스트 조회
class EstimationSerializer(serializers.ModelSerializer):
    expert = ExpertDetailSerializer(read_only=True)

    class Meta:
        model = Estimation
        fields = [
            "id",
            "request",
            "expert",
            "location",
            "due_date",
            "service",
            "charge",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "expert", "created_at", "updated_at"]


# 견적 상세 조회
class EstimationRetrieveSerializer(serializers.ModelSerializer):
    expert = ExpertDetailSerializer(read_only=True)
    request = EstimationsRequestSerializer(read_only=True)

    class Meta:
        model = Estimation
        fields = ["id", "request", "expert", "location", "due_date", "service", "charge", "created_at", "updated_at"]
        read_only_fields = ["id", "request", "expert", "service", "created_at", "updated_at"]
