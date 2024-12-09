from django.urls import path

from reservations import views

urlpatterns = [
    path("", views.ExpertReservationListAPIView.as_view(), name="expert-reservation-list"),
    path(
        "<int:reservation_id>/",
        views.ExpertReservationDetailAPIView.as_view(),
        name="expert-reservation-detail",
    ),
    path("schedule/", views.ReservationListForCalendarAPIView.as_view(), name="reservation-list-for-calendar"),
]
