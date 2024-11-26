from django.urls import path

from reviews.views.expert_views import ReviewListViewForExpert

urlpatterns = [
    path("", ReviewListViewForExpert.as_view(), name="expert-review-list"),
]
