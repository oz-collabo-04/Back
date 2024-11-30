from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from common.constants.choices import AREA_CHOICES, SERVICE_CHOICES
from expert.models import Career, Expert


class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = ["id", "title", "description", "start_date", "end_date"]


class ExpertSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    careers = CareerSerializer(many=True)
    service_display = serializers.SerializerMethodField()
    available_location_display = serializers.SerializerMethodField()

    class Meta:
        model = Expert
        fields = [
            "user",
            "id",
            "expert_image",
            "service",
            "service_display",
            "standard_charge",
            "appeal",
            "available_location",
            "available_location_display",
            "careers",
        ]
        read_only_fields = (
            "user",
            "id",
        )

    @extend_schema_field(
        {
            "type": "object",
            "properties": {"id": {"type": "integer"}, "name": {"type": "string"}, "gender": {"type": "string"}},
        }
    )
    def get_user(self, instance):
        """
        전문가와 연관된 사용자 정보를 반환합니다.
        """
        user = instance.user
        return {
            "id": user.id,
            "name": user.name,
            "gender": user.gender,
        }

    @extend_schema_field({"type": "string", "example": "결혼식 사회자"})
    def get_service_display(self, obj):
        """
        service 필드의 키 값을 한글로 변환하여 반환합니다.
        """
        return dict(SERVICE_CHOICES).get(obj.service, obj.service)

    @extend_schema_field({"type": "array", "items": {"type": "string", "example": "서울특별시"}})
    def get_available_location_display(self, obj):
        """
        available_location 필드는 AREA_CHOICES 키에 해당하는 값을 반환합니다.
        """
        if obj.available_location:
            mapped_locations = [dict(AREA_CHOICES).get(location, location) for location in obj.available_location]
            return mapped_locations
        return []

    @extend_schema_field(serializers.ListSerializer(child=CareerSerializer()))
    def get_careers(self, instance):
        """
        전문가와 연결된 모든 Career 객체를 반환합니다.
        """
        careers = instance.career_set.all()
        return CareerSerializer(careers, many=True).data

    def validate_careers(self, value):
        """
        careers 필드의 데이터 유효성 검증.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("careers 데이터는 딕셔너리 리스트여야 합니다.")
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("careers 리스트의 각 항목은 딕셔너리여야 합니다.")
        return value

    def create(self, validated_data):
        """
        전문가 생성 시 경력사항을 함께 생성하기 위해 transaction 사용.
        """
        careers_data = validated_data.pop("careers", [])
        user = self.context["request"].user
        validated_data.pop("user", None)  # user 필드 제거

        with transaction.atomic():
            # Expert 객체 생성
            expert = Expert.objects.create(user=user, **validated_data)

            # Career 객체 생성
            Career.objects.bulk_create([
                Career(expert=expert, **career) for career in careers_data
            ])

            # 사용자 상태를 전문가로 설정
            user.is_expert = True
            user.save()

            return expert

    def update(self, instance, validated_data):
        """
        전문가 생성 시 경력사항을 함께 생성하기 위해 transaction 사용.
        """
        careers_data = validated_data.pop("careers", [])

        with transaction.atomic():
            # 기존의 전문가 커리어 삭제
            Career.objects.filter(expert=instance).delete()

            # 새로운 Career 객체 생성
            Career.objects.bulk_create([
                Career(expert=instance, **career) for career in careers_data
            ])

            instance = super().update(instance, validated_data)

            return instance


    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if isinstance(instance.available_location, str):
            location_list = instance.available_location.split(", ")
            ret["available_location_display"] = [
                dict(AREA_CHOICES).get(location) for location in location_list
            ]

        return ret