import random

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from estimations.models import RequestManager
from expert.models import Career, Expert
from expert.seriailzers import (
    CareerSerializer,
    ExpertCreateSerializer,
    ExpertDetailSerializer,
    RequestManagerSerializer,
)


# 전문가 전환 - 전문가 정보 생성
class ExpertCreateView(CreateAPIView):
    queryset = Expert.objects.all()
    serializer_class = ExpertCreateSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Expert"],
        summary="전문가 전환 - expert 생성 - 본인만",
        responses={200: ExpertCreateSerializer()},
    )
    def post(self, request, *args, **kwargs):
        # 현재 사용자가 이미 전문가인지 확인
        user = request.user
        if user.is_expert:
            return Response({"detail": "이미 전문가 전환이 되어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 전문가로 전환
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # 현재 요청한 사용자를 user로 설정하여 저장
        serializer.save(user=self.request.user)


# 전문가 리스트 조회 - 누구나
class ExpertListView(ListAPIView):
    serializer_class = ExpertDetailSerializer
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
            )
        ],
        responses={200: ExpertDetailSerializer()},
    )
    def get(self, request, *args, **kwargs):
        service_name = request.query_params.get("service")
        if not service_name:
            return Response({"detail": "서비스명을 제공해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        experts = Expert.objects.filter(service=service_name).prefetch_related("career_set")

        # 3명의 전문가를 랜덤으로 선택
        expert_list = list(experts)
        random.shuffle(expert_list)
        limited_experts = expert_list[:3]

        serializer = self.get_serializer(limited_experts, many=True)
        return Response(serializer.data)


class ExpertDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Expert.objects.all()
    serializer_class = ExpertDetailSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Expert"],
        summary="전문가 상세 조회 - 누구나",
        responses={200: ExpertDetailSerializer()},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Expert"],
        summary="전문가 정보 전체 수정 - 본인만",
        responses={200: ExpertDetailSerializer()},
    )
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        # 전문가 ID가 로그인한 사용자와 일치하는지 확인
        if request.user != instance.user:
            raise PermissionDenied("자신의 정보만 수정할 수 있습니다.")
        return self.update(request, *args, **kwargs)

    @extend_schema(
        tags=["Expert"],
        summary="전문가 정보 부분 수정 - 본인만",
        responses={200: ExpertDetailSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.user:
            raise PermissionDenied("자신의 정보만 수정할 수 있습니다.")
        return self.update(request, *args, **kwargs)


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

    @extend_schema(
        tags=["Expert"],
        summary="전문가 경력 일괄 수정 - 본인만 // 이게 필요한가요??",
        responses=CareerSerializer(),
    )
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        # 로그인한 사용자와 경력의 소유자가 일치하는지 확인
        if request.user != instance.expert.user:
            raise PermissionDenied("본인의 경력 정보만 수정할 수 있습니다.")
        return self.update(request, *args, **kwargs)


class CareerDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Career.objects.all()
    serializer_class = CareerSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Expert"],
        summary="특정 커리어 정보수정 - 본인만",
        responses={200: CareerSerializer()},
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance.expert.user:
            raise PermissionDenied("본인의 경력 정보만 수정할 수 있습니다.")
        return self.partial_update(request, *args, **kwargs)  # partial_update를 사용하여 PATCH 처리

    @extend_schema(
        tags=["Expert"],
        summary="전문가 경력 삭제 - 본인만",
        responses={204: OpenApiTypes.NONE},
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        # 로그인한 사용자와 경력의 소유자가 일치하는지 확인
        if request.user != instance.expert.user:
            raise PermissionDenied("본인의 경력 정보만 삭제할 수 있습니다.")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)  # 명시적으로 204 응답 반환

