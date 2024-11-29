from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated

from common.exceptions import BadRequestException
from common.permissions.expert_permissions import IsExpert
from estimations.models import Estimation, EstimationsRequest, RequestManager
from estimations.serializers.expert_serializers import (
    EstimationCreateByExpertSerializer,
    EstimationListForExpertSerializer,
    EstimationRequestListForExpertSerializer,
    EstimationUpdateByExpertSerializer,
)


@extend_schema(tags=["estimation-expert"], summary="유저의 견적 요청에 대해서 전문가가 견적을 생성")
class EstimationCreateByExpertAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated, IsExpert)
    serializer_class = EstimationCreateByExpertSerializer

    def perform_create(self, serializer):
        serializer.save(expert=self.request.user.expert)


@extend_schema(tags=["estimation-expert"], summary="전문가가 자신이 내려준 견적을 params로 필터링 하여 리스트 확인")
class EstimationListByExpertAPIView(ListAPIView):
    permission_classes = (IsAuthenticated, IsExpert)
    serializer_class = EstimationListForExpertSerializer

    def get_queryset(self):
        filter_status = ["pending", "confirmed"]
        queryset = Estimation.objects.filter(
            expert=self.request.user.expert, reservation__isnull=False, reservation__status__in=filter_status
        )
        year = self.request.query_params.get("year", None)
        month = self.request.query_params.get("month", None)
        if (not year and month) or (not month and year):
            return BadRequestException("month와 year는 같이 제출되어야합니다.")

        if year and month:
            queryset = queryset.filter(due_date__year=year, due_date__month=month)

        return queryset


class EstimationUpdateByExpertAPIView(UpdateAPIView):
    permission_class = (IsAuthenticated, IsExpert)
    serializer_class = EstimationUpdateByExpertSerializer
    queryset = Estimation.objects.all()
    lookup_field = "estimation_id"

    def get_object(self):
        object = get_object_or_404(self.queryset, id=self.kwargs[self.lookup_field], expert=self.request.user.expert)
        return object

    @extend_schema(tags=["estimation-expert"], summary="전문가가 내준 견적 중 특정 견적을 전체 수정")
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(tags=["estimation-expert"], summary="전문가가 내준 견적 중 특정 견적을 부분 수정")
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@extend_schema(tags=["estimation-expert"], summary="전문가가 받은 견적 요청 리스트를 조회")
class EstimationRequestListForExpertAPIView(ListAPIView):
    permission_class = (IsAuthenticated, IsExpert)
    serializer_class = EstimationRequestListForExpertSerializer

    def get_queryset(self):
        queryset = RequestManager.objects.filter(expert=self.request.user.expert)

        return queryset


@extend_schema(tags=["estimation-expert"], summary="전문가가 받은 견적 요청 기록을 삭제")
class RequestManagerDestroyAPView(DestroyAPIView):
    permission_classes = (IsAuthenticated, IsExpert)
    lookup_field = "id"
    lookup_url_kwarg = "request_id"
    queryset = RequestManager.objects.all()
