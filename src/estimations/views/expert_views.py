from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from common.permissions.expert_permissions import IsExpert
from estimations.models import Estimation
from estimations.serializers.expert_serializers import (
    EstimationCreateByExpertSerializer,
    EstimationUpdateByExpertSerializer
)

@extend_schema(tags=['estimation-expert'])
class EstimationCreateByExpertAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated, IsExpert)
    serializer_class = EstimationCreateByExpertSerializer

    def perform_create(self, serializer):
        serializer.save(expert=self.request.user.expert)


@extend_schema(tags=['estimation-expert'])
class EstimationUpdateByExpertAPIView(UpdateAPIView):
    permission_class = (IsAuthenticated, IsExpert)
    serializer_class = EstimationUpdateByExpertSerializer
    queryset = Estimation.objects.all()
    lookup_field = "estimation_id"

    def get_object(self):
        object = get_object_or_404(self.queryset, id=self.kwargs[self.lookup_field], expert=self.request.user.expert)
        return object