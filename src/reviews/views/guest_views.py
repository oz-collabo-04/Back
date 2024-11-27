from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from reviews.models import Review
from reviews.serializers.guest_seriailzers import ReviewSerializer


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(reservation__estimation__request__user=self.request.user)

    @extend_schema(
        tags=["guests-reviews"],
        summary="게스트가 작성한 자신의 리뷰 리스트를 조회",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        tags=["guests-reviews"],
        summary="게스트가 견적 서비스 이용 후 리뷰를 작성",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@extend_schema(
    tags=["guests-reviews"],
    summary="유저가 전문가로부터 받은 견적 상세 조회 시 하단의 리뷰 리스트 반환",
)
class ReviewListByExpertAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        expert_id = self.kwargs["expert_id"]
        if not expert_id:
            raise ValidationError(detail="expert_id 가 제공되지 않았습니다.")
        queryset = Review.objects.filter(reservation__estimation__expert_id=expert_id).order_by("-created_at")
        return queryset


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = "id"
    lookup_url_kwarg = "review_id"

    @extend_schema(
        tags=["guests-reviews"],
        summary="게스트가 작성한 자신의 리뷰중 특정 리뷰 삭제",
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "리뷰가 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        tags=["guests-reviews"],
        summary="게스트가 작성한 자신의 리뷰중 특정 리뷰를 상세 조회",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["guests-reviews"],
        summary="게스트가 작성한 자신의 리뷰중 특정 리뷰를 부분 수정",
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["guests-reviews"],
        summary="게스트가 작성한 자신의 리뷰중 특정 리뷰를 전체 수정",
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
