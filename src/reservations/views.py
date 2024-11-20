from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from estimations.models import Estimation
from reservations.models import Reservation
from reservations.seriailzers import (
    ReservationCreateSerializer,
    ReservationInfoSerializer,
)


class ReservationListAPIView(generics.ListAPIView):
    queryset = Reservation.objects.all().prefetch_related(
        "estimation", "estimation__request", "estimation__request__user", "estimation__expert"
    )
    serializer_class = ReservationInfoSerializer
    permission_classes = [AllowAny]


class ReservationCreateAPIView(generics.CreateAPIView):
    queryset = Reservation.objects.all().prefetch_related(
        "estimation", "estimation__request", "estimation__request__user", "estimation__expert"
    )
    serializer_class = ReservationCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(status="pending")


class ReservationRetrieveUpdateAPIView(generics.GenericAPIView, RetrieveModelMixin, UpdateModelMixin):
    queryset = Reservation.objects.all().prefetch_related(
        "estimation", "estimation__request", "estimation__request__user", "estimation__expert"
    )
    serializer_class = ReservationInfoSerializer
    permission_classes = [AllowAny]
    lookup_field = "reservation_id"  # URL에서 <int:reservation_id> 부분과 매칭

    def get_object(self):
        return get_object_or_404(queryset=self.queryset, id=self.kwargs[self.lookup_field])

    def update(self, request, *args, **kwargs):
        reservation = self.get_object()
        if reservation.status == "completed":  # 예: 완료된 예약 상태에 대한 예외 처리
            return Response({"detail": "완료된 예약은 상태를 변경할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
