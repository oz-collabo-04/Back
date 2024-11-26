from django.urls import path

from reviews.views import guest_views

urlpatterns = [
    path("", guest_views.ReviewListCreateAPIView.as_view(), name="review-list-create"),
    path("experts/<int:expert_id>/", guest_views.ReviewListByExpertAPIView.as_view(), name="expert-review-list"),
    path("<int:review_id>/", guest_views.ReviewDetailAPIView.as_view(), name="review-detail"),
]
