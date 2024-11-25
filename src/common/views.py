from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants.choices import AREA_CHOICES, SERVICE_CHOICES


class ServiceChoicesView(APIView):
    """
    서비스 목록을 반환하는 API
    """

    @extend_schema(
        tags=["Service"],
        summary="가능한 서비스 목록 조회 - 누구나",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "services": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "example": "mc"},
                                "label": {"type": "string", "example": "MC"},
                            },
                        },
                    }
                },
            },
            500: {
                "type": "object",
                "properties": {"detail": {"type": "string", "example": "오류가 발생했습니다."}},
            },
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            services = [{"key": key, "label": label} for key, label in SERVICE_CHOICES]
            return Response({"services": services}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LocationChoicesView(APIView):
    """
    지역 목록을 반환하는 API
    """

    @extend_schema(
        tags=["Service"],
        summary="서비스 가능 지역 목록 조회 - 누구나",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "areas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "example": "seoul"},
                                "label": {"type": "string", "example": "서울"},
                            },
                        },
                    }
                },
            },
            500: {
                "type": "object",
                "properties": {"detail": {"type": "string", "example": "오류가 발생했습니다."}},
            },
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            areas = [{"key": key, "label": label} for key, label in AREA_CHOICES]
            return Response({"areas": areas}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
