from django.urls import path

from expert.views import (
    CareerDetailView,
    CareerListViews,
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

]
