from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated

from estimations.models import Estimation, EstimationsRequest
from estimations.seriailzers import (
    EstimationRetrieveSerializer,
    EstimationSerializer,
    EstimationsRequestSerializer,
)


class EstimationListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EstimationSerializer

    def get_queryset(self):
        return Estimation.objects.filter(request__user=self.request.user)


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


class EstimationRequestDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EstimationsRequestSerializer
    queryset = Estimation.objects.all()
    lookup_field = "estimation_id"

    def get_object(self):
        object = get_object_or_404(self.queryset, id=self.kwargs[self.lookup_field], user=self.request.user)
        print(self.request.user.id)
        return object

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        response.data["detail"] = "사용자의 견적 요청 기록이 성공적으로 삭제되었습니다."
        return response
