from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from common.permissions.expert_permissions import IsExpert
from reservations.models import Reservation
from reservations.seriailzers import (
    ExpertReservationInfoSerializer,
    ReservationCreateSerializer,
    ReservationInfoSerializer,
)


class ReservationListAPIView(generics.ListAPIView):

    queryset = Reservation.objects.all().prefetch_related(
        "estimation", "estimation__request", "estimation__request__user", "estimation__expert"
    )
    serializer_class = ReservationInfoSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["reservations"],
        summary="게스트의 예약 리스트 조회",
        responses={200: ReservationInfoSerializer},
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ReservationCreateAPIView(generics.CreateAPIView):
    queryset = Reservation.objects.all().prefetch_related(
        "estimation", "estimation__request", "estimation__request__user", "estimation__expert"
    )
    serializer_class = ReservationCreateSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["reservations"],
        summary="게스트의 예약 생성",
        responses={201: ReservationCreateSerializer},
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ReservationRetrieveUpdateAPIView(generics.GenericAPIView, RetrieveModelMixin, UpdateModelMixin):
    queryset = Reservation.objects.all().prefetch_related(
        "estimation", "estimation__request", "estimation__request__user", "estimation__expert"
    )
    serializer_class = ReservationInfoSerializer
    permission_classes = [AllowAny]
    lookup_field = "reservation_id"

    def get_object(self):
        return get_object_or_404(queryset=self.queryset, id=self.kwargs[self.lookup_field])

    @extend_schema(
        tags=["reservations"],
        summary="게스트의 예약 상세 조회",
        responses={200: ReservationInfoSerializer},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["reservations"],
        summary="게스트의 예약 상태 변경 - 전체 수정",
        responses={200: ReservationCreateSerializer},
    )
    def put(self, request, *args, **kwargs):
        reservation = self.get_object()
        if reservation.status == "completed":
            return Response({"detail": "완료된 예약은 상태를 변경할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["reservations"],
        summary="게스트의 예약 상태 변경 - 부분 수정",
        responses={200: ReservationCreateSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ExpertReservationListAPIView(generics.ListAPIView):
    serializer_class = ExpertReservationInfoSerializer
    permission_classes = [IsExpert]

    def get_queryset(self):
        expert = self.request.user.expert
        return Reservation.objects.filter(estimation__expert=expert).prefetch_related(
            "estimation", "estimation__request", "estimation__request__user", "estimation__expert"
        )


class ExpertReservationDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ExpertReservationInfoSerializer
    permission_classes = [IsExpert]
    lookup_field = "id"

    def get_queryset(self):
        expert = self.request.user.expert
        return Reservation.objects.filter(estimation__expert=expert).prefetch_related(
            "estimation", "estimation__request", "estimation__request__user", "estimation__expert"
        )
