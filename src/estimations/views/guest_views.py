from drf_spectacular.utils import extend_schema
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated

from estimations.models import Estimation, EstimationsRequest
from estimations.serializers.guest_seriailzers import (
    EstimationRetrieveSerializer,
    EstimationSerializer,
    EstimationsRequestSerializer,
)


@extend_schema(tags=["estimations-user"], summary="유저가 견적 요청 후 전문가로 부터 받은 견적 조회")
class EstimationListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EstimationSerializer

    def get_queryset(self):
        return Estimation.objects.filter(request__user=self.request.user)


@extend_schema(tags=["estimations-user"], summary="유저가 견적 요청 후 전문가로 부터 받은 견적 중 특정 견적을 조회")
class EstimationRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EstimationRetrieveSerializer
    queryset = Estimation.objects.all()
    lookup_field = "estimation_id"

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.kwargs[self.lookup_field], request__user=self.request.user)


class EstimationRequestListCreateAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EstimationsRequestSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        status = query_params.get("status")

        if status:
            requests = EstimationsRequest.objects.filter(user=self.request.user, status=status)
            return requests

        requests = EstimationsRequest.objects.filter(user=self.request.user).prefetch_related("user")
        return requests

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(tags=["estimations-user"], summary="유저의 견적 요청 리스트 조회")
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(tags=["estimations-user"], summary="유저의 견적 요청 생성")
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class EstimationRequestDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EstimationsRequestSerializer
    queryset = EstimationsRequest.objects.all()
    lookup_field = "request_id"

    def get_object(self):
        object = get_object_or_404(self.queryset, id=self.kwargs[self.lookup_field], user=self.request.user)
        return object

    @extend_schema(tags=["estimations-user"], summary="유저의 견적 요청 중 특정 요청을 상세 조회")
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(tags=["estimations-user"], summary="유저의 견적 요청 중 특정 요청을 전체 수정")
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(tags=["estimations-user"], summary="유저의 견적 요청 중 특정 요청을 일부 수정")
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(tags=["estimations-user"], summary="유저의 견적 요청 중 특정 요청을 삭제")
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        response.data["detail"] = "사용자의 견적 요청 기록이 성공적으로 삭제되었습니다."
        return response
