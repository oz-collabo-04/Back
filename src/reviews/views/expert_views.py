from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.permissions.expert_permissions import IsExpert
from reviews.models import Review
from reviews.serializers.expert_serializers import ReviewListSerializer


class ReviewListViewForExpert(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsExpert]
    serializer_class = ReviewListSerializer

    @extend_schema(tags=["experts-reviews"], summary="전문가의 자신의 서비스에 대한 리뷰 목록 조회")
    def get_queryset(self):
        return Review.objects.filter(reservation__estimation__request__user=self.request.user)
