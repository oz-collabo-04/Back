from django.urls import path

from estimations.views.expert_views import (
    EstimationCreateByExpertAPIView,
    EstimationListByExpertAPIView,
    EstimationRequestListForExpertAPIView,
    EstimationUpdateByExpertAPIView,
    RequestManagerDestroyAPView,
)

urlpatterns = [
    path("", EstimationCreateByExpertAPIView.as_view(), name="expert-estimation-create"),
    path("list/", EstimationListByExpertAPIView.as_view(), name="expert-estimation-list"),
    path("<int:estimation_id>/", EstimationUpdateByExpertAPIView.as_view(), name="expert-estimation-update"),
    path("requests/", EstimationRequestListForExpertAPIView.as_view(), name="expert-estimation-request-list"),
    path("requests/<int:request_id>/", RequestManagerDestroyAPView.as_view(), name="expert-request-destroy"),
]
