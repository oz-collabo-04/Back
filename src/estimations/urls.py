from django.urls import path

from estimations.views import (
    EstimationListAPIView,
    EstimationRequestDetailAPIView,
    EstimationRequestListCreateAPIView,
    EstimationRetrieveAPIView,
)

urlpatterns = [
    # 게스트 유저의 생성 및 목록 조회
    path("", EstimationListAPIView.as_view(), name="estimation-list-create"),
    # 게스트 유저의 견적 상세 조회
    path("<int:estimation_id>/", EstimationRetrieveAPIView.as_view(), name="estimation-detail"),
    # 게스트 유저의 견적 요청 생성 및 리스트 조회
    path("request/", EstimationRequestListCreateAPIView.as_view(), name="create-estimation"),
    # 게스트 유저의 견적 요청 상세 조회, 상세 수정 및 삭제
    path("request/<request_id>/", EstimationRequestDetailAPIView.as_view(), name="create-estimation"),
]
