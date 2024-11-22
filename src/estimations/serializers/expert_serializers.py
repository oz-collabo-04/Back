from rest_framework import serializers

from estimations.models import Estimation


# 유저의 요청에 대한 전문가의 견적 등록 요청
class EstimationCreateByExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estimation
        fields = [
            "id",
            "request",
            "expert",
            "due_date",
            "service",
            "charge",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ("id", "expert", "created_at", "updated_at")


# 유저의 요청에 대한 전문가의 견적 수정 요청
class EstimationUpdateByExpertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estimation
        fields = [
            "id",
            "request",
            "expert",
            "due_date",
            "service",
            "charge",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ("id", "request", "expert", "created_at", "updated_at")