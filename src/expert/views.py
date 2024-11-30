import json
import random

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import BadRequestException
from expert.models import Career, Expert
from expert.seriailzers import CareerSerializer, ExpertSerializer


# 전문가 전환 - 전문가 정보 생성
class ExpertCreateView(CreateAPIView):
    queryset = Expert.objects.all()
    serializer_class = ExpertSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=["Expert"],
        summary="전문가 전환 - expert 생성 - 본인만",
        responses={200: ExpertSerializer()},
    )
    def post(self, request, *args, **kwargs):
        # 현재 사용자가 이미 전문가인지 확인
        user = request.user
        if user.is_expert:
            return Response({"detail": "이미 전문가 전환이 되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)
        careers = request.data.get("careers", [])
        if careers:
            careers = json.loads(careers)

        request_data = {
            "available_location": request.data.getlist("available_location", []),
            "appeal": request.data.get("appeal", []),
            "service": request.data.get("service", []),
            "careers": careers,
            "expert_image": request.data.get("expert_image", []),
        }

        # 전문가로 전환
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # 현재 요청한 사용자를 user로 설정하여 저장
        serializer.save(user=self.request.user)


# 전문가 -> 유저 전환
class ExpertDeactivatedView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Expert"],
        summary="전문가 -> 유저 전환",
        description="현재 로그인된 사용자가 전문가에서 일반 유저로 전환합니다.",
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request, *args, **kwargs):
        # 현재 사용자가 이미 유저 인지 확인
        user = request.user
        if not user.is_expert:
            return Response({"detail": "이미 유저로 되어있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 유저로 전환
        user.is_expert = False
        user.save()
        return Response({"detail": "유저로 전환 되었습니다."}, status=status.HTTP_200_OK)


# 전문가 리스트 조회 - 누구나
class ExpertListView(ListAPIView):
    serializer_class = ExpertSerializer
    permission_classes = [
        AllowAny,
    ]

    @extend_schema(
        tags=["Expert"],
        summary="전문가 목록 조회 - 누구나",
        parameters=[
            OpenApiParameter(
                name="service",
                description="서비스명으로 전문가를 필터링 합니다.(예: mc, snap 등)",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="random",
                description="랜덤 조회 여부 (random=True: 3명만 랜덤 조회, random=False: 전체 조회)",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
        ],
        responses={200: ExpertSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        service_name = request.query_params.get("service")
        random_query = request.query_params.get("random", "false").lower()

        if not service_name:
            return Response({"detail": "서비스명을 제공해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 서비스명으로 필터링
        experts = Expert.objects.filter(service=service_name).prefetch_related("careers")

        # 랜덤 조회 여부 확인
        if random_query == "true":
            # 랜덤으로 3명의 전문가를 반환
            experts = list(experts)
            random.shuffle(experts)
            experts = experts[:3]

        serializer = self.get_serializer(experts, many=True)
        return Response(serializer.data)


class ExpertDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ExpertSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # 현재 로그인한 사용자와 연결된 Expert 객체 가져오기
        try:
            return Expert.objects.get(user=self.request.user)
        except Expert.DoesNotExist:
            raise PermissionDenied("전문가 정보를 찾을 수 없습니다.")

    @extend_schema(
        tags=["Expert"],
        summary="전문가 상세 조회 - 로그인한 본인만",
        responses={200: ExpertSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Expert"],
        summary="전문가 정보 전체 수정 - 본인만",
        responses={200: ExpertSerializer()},
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        request_data = {}

        careers = request.data.get("careers", [])
        if careers:
            careers = json.loads(careers)
            request_data["careers"] = careers

        available_location = request.data.getlist("available_location", [])
        if available_location:
            request_data["available_location"] = available_location

        appeal = request.data.get("appeal", "")
        if appeal:
            request_data["appeal"] = appeal

        service = request.data.get("service", "")
        if service:
            request_data["service"] = service

        expert_image = request.data.get("expert_image", None)
        if expert_image:
            request_data["expert_image"] = expert_image

        if not request_data:
            raise BadRequestException("아무런 데이터도 제공되지 않았습니다.")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @extend_schema(
        tags=["Expert"],
        summary="전문가 정보 부분 수정 - 본인만",
        responses={200: ExpertSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["X"],
        summary="소프트 딜리트 사용으로 - 사용하지 않는 api",
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CareerListViews(ListCreateAPIView):
    serializer_class = CareerSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # URL 경로에서 expert_id를 가져와 필터링
        expert_id = self.kwargs.get("expert_id")
        return Career.objects.filter(expert_id=expert_id)

    @extend_schema(
        tags=["Expert"],
        summary="전문가 경력 리스트 - 로그인된 누구나",
        responses={200: CareerSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        tags=["Expert"],
        summary="전문가 경력 생성 - 본인만",
        responses={201: CareerSerializer()},
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        # 전문가 여부 확인
        if not user.is_expert:
            return Response({"detail": "전문가만 경력을 추가할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)

        # URL에서 expert_id를 가져옴
        expert_id = self.kwargs.get("expert_id")
        try:
            expert = Expert.objects.get(id=expert_id, user=user)
        except Expert.DoesNotExist:
            return Response(
                {"detail": "본인의 전문가 프로필에만 경력을 추가할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )

        # 경력 생성 시 expert 필드를 설정
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(expert=expert)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
