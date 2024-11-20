from django.urls import path

from reservations import views

urlpatterns = [
    path("", views.ReservationListAPIView.as_view(), name="reservation-list"),
    path("create/", views.ReservationCreateAPIView.as_view(), name="reservation-create"),
    path("<int:reservation_id>/", views.ReservationRetrieveUpdateAPIView.as_view(), name="reservation-retrieve-update"),
]
