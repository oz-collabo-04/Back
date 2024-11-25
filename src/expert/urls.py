from django.urls import path

from expert.views import (
    CareerDetailView,
    CareerListViews,
    EstimationsRequestDeleteView,
    EstimationsRequestListViews,
    ExpertCreateView,
    ExpertDetailView,
    ExpertListView,
)

app_name = "experts"
urlpatterns = [
    path("", ExpertListView.as_view(), name="expert_list"),
    path("register/", ExpertCreateView.as_view(), name="expert_register"),
    # path("/<int:pk>",)
    path("<int:pk>/", ExpertDetailView.as_view(), name="expert_detail"),
    path("<int:expert_id>/careers/", CareerListViews.as_view(), name="expert_careers"),
    path("<int:expert_id>/careers/<int:pk>/", CareerDetailView.as_view(), name="career_detail"),
    path("<int:expert_id>/estimations/request/", EstimationsRequestListViews.as_view(), name="expert_request_list"),
    path(
        "<int:expert_id>/estimations/request/<int:pk>/",
        EstimationsRequestDeleteView.as_view(),
        name="expert_request_delete",
    ),
]
