from django.urls import path

from expert.views import (
    CareerListViews,
    ExpertCreateView,
    ExpertDeactivatedView,
    ExpertDetailView,
    ExpertListView,
)

app_name = "experts"
urlpatterns = [
    path("", ExpertListView.as_view(), name="expert_list"),
    path("register/", ExpertCreateView.as_view(), name="expert_register"),
    path("deactivate/", ExpertDeactivatedView.as_view(), name="expert_deactivate"),
    # path("/<int:pk>",)
    path("<int:pk>/", ExpertDetailView.as_view(), name="expert_detail"),
    path("<int:expert_id>/careers/", CareerListViews.as_view(), name="expert_careers"),
]
