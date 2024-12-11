from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone
from rest_framework import fields, serializers

from common.constants.choices import AREA_CHOICES, SERVICE_CHOICES
from estimations.models import Estimation, EstimationsRequest
from expert.models import Expert
from expert.seriailzers import CareerSerializer
from reviews.models import Review
from users.models import User


class ExpertUserSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "phone_number", "gender", "gender_display"]
        read_only_fields = ["id", "name", "email", "phone_number", "gender", "gender_display"]


class EstimationExpertSerializer(serializers.ModelSerializer):
    user = ExpertUserSerializer(read_only=True)
    careers = CareerSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()
    service_display = serializers.CharField(source="get_service_display", read_only=True)
    available_location_display = serializers.CharField(source="get_available_location_display", read_only=True)

    class Meta:
        model = Expert
        fields = (
            "id",
            "rating",
            "expert_image",
            "service",
            "service_display",
            "standard_charge",
            "appeal",
            "available_location",
            "available_location_display",
            "user",
            "careers",
        )
        read_only_fields = (
            "id",
            "rating",
            "expert_image",
            "service",
            "service_display",
            "standard_charge",
            "appeal",
            "available_location",
            "available_location_display",
            "user",
            "careers",
        )

    def get_rating(self, obj):
        average_rating = (
            Review.objects.filter(reservation__estimation__expert_id=obj.id).aggregate(average_rating=Avg("rating"))[
                "average_rating"
            ]
            or 0.0
        )
        return round(average_rating, 1)


class EstimationsRequestSerializer(serializers.ModelSerializer):
    service_list = fields.MultipleChoiceField(choices=SERVICE_CHOICES)
    service_list_display = fields.CharField(source="get_service_list_display", read_only=True)
    prefer_gender_display = fields.CharField(source="get_prefer_gender_display", read_only=True)
    location_display = fields.CharField(source="get_location_display", read_only=True)
    status_display = fields.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = EstimationsRequest
        fields = [
            "id",
            "user",
            "service_list",
            "service_list_display",
            "prefer_gender",
            "prefer_gender_display",
            "wedding_hall",
            "wedding_datetime",
            "is_reception",
            "location",
            "location_display",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "service_list_display",
            "location_display",
            "prefer_gender_display",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]

    def validate_wedding_datetime(self, value):
        today = timezone.now() + timedelta(days=7)
        if value < today:
            raise serializers.ValidationError("결혼식 진행 예정일은 오늘로부터 7일 이후여야 합니다.")
        return value


# 견적 리스트 조회
class EstimationSerializer(serializers.ModelSerializer):
    expert = EstimationExpertSerializer(read_only=True)
    service_display = serializers.CharField(source="get_service_display", read_only=True)
    location_display = serializers.CharField(source="get_location_display", read_only=True)

    class Meta:
        model = Estimation
        fields = [
            "id",
            "request",
            "expert",
            "location",
            "location_display",
            "due_date",
            "service",
            "service_display",
            "description",
            "charge",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "request",
            "expert",
            "location",
            "location_display",
            "due_date",
            "service",
            "service_display",
            "description",
            "charge",
            "created_at",
            "updated_at",
        ]


# 견적 상세 조회
class EstimationRetrieveSerializer(serializers.ModelSerializer):
    expert = EstimationExpertSerializer(read_only=True)
    request = EstimationsRequestSerializer(read_only=True)
    service_display = serializers.CharField(source="get_service_display", read_only=True)
    location_display = serializers.CharField(source="get_location_display", read_only=True)

    class Meta:
        model = Estimation
        fields = [
            "id",
            "request",
            "expert",
            "location",
            "location_display",
            "due_date",
            "service",
            "service_display",
            "description",
            "charge",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "request",
            "expert",
            "location",
            "location_display",
            "due_date",
            "service",
            "service_display",
            "description",
            "charge",
            "created_at",
            "updated_at",
        ]
