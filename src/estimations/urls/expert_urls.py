from django.urls import path

from estimations.views.expert_views import (
    EstimationCreateByExpertAPIView,
    EstimationUpdateByExpertAPIView
)

urlpatterns = [
    path("", EstimationCreateByExpertAPIView.as_view(), name="expert-estimation-create"),
    path("<int:estimation_id>/", EstimationUpdateByExpertAPIView.as_view(), name="expert-estimation-update"),
]