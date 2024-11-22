import json

from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from expert.models import Career, Expert


class CareerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Career
        fields = ["id", "title", "description", "start_date", "end_date"]


# 전문가 생성 시리얼라이저
# 전문가 생성되면서 경력사항이 같이 생성되야해서 transaction사용
class ExpertCreateSerializer(serializers.ModelSerializer):
    # 입력만을 위한 필드
    careers = serializers.CharField(write_only=True)

    class Meta:
        model = Expert
        fields = [
            "user",
            "id",
            "expert_image",
            "service",
            "standard_charge",
            "appeal",
            "available_location",
            "careers",
        ]
        read_only_fields = (
            "user",
            "id",
        )

    # careers 필드의 데이터 유효성 검증
    def validate_careers(self, value):
        # careers 필드가 JSON 문자열로 전달될 경우 처리
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("careers 데이터는 올바른 JSON 형식이어야 합니다.")
            if not isinstance(parsed, list):
                raise serializers.ValidationError("careers 데이터는 딕셔너리 리스트여야 합니다.")
            for item in parsed:
                if not isinstance(item, dict):
                    raise serializers.ValidationError("careers 리스트의 각 항목은 딕셔너리여야 합니다.")
            return parsed
        raise serializers.ValidationError("careers 필드의 데이터 형식이 잘못되었습니다. JSON 문자열이어야 합니다.")

    def create(self, validated_data):
        # careers 데이터를 처리
        careers_data = validated_data.pop("careers", [])
        user = self.context["request"].user
        validated_data.pop("user", None)  # user 필드 제거

        with transaction.atomic():
            # Expert 객체 생성
            expert = Expert.objects.create(user=user, **validated_data)

            # Career 객체 생성
            for career in careers_data:
                if not isinstance(career, dict):
                    raise serializers.ValidationError({"careers": "careers 리스트의 각 항목은 딕셔너리여야 합니다."})
                Career.objects.create(expert=expert, **career)

            # 사용자 상태를 전문가로 설정
            user.is_expert = True
            user.save()

        return expert


# 디테일 추가 예정 - 별점 등..
# 전문가 디테일 페이지
class ExpertDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    careers = serializers.SerializerMethodField()

    class Meta:
        model = Expert
        fields = [
            "user",
            "id",
            "expert_image",
            "service",
            "standard_charge",
            "appeal",
            "available_location",
            "careers",
        ]
        read_only_fields = (
            "user",
            "id",
        )

    @extend_schema_field(serializers.CharField)
    def get_user(self, instance):
        # `instance.user`를 통해 관련 사용자 정보를 가져옵니다.
        user = instance.user
        return {
            "id": user.id,
            "name": user.name,
            "gender": user.gender,
        }

    @extend_schema_field(serializers.ListSerializer(child=CareerSerializer()))
    def get_careers(self, instance):
        # 역참조를 통해 관련 Career 객체를 가져옴
        # `career_set`은 ForeignKey의 기본 역참조 이름
        careers = instance.career_set.all()
        return CareerSerializer(careers, many=True).data
