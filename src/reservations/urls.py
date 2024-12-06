from django.urls import path

from reservations import views

urlpatterns = [
    path("", views.ReservationListAPIView.as_view(), name="reservation-list"),
    path("create/", views.ReservationCreateAPIView.as_view(), name="reservation-create"),
    path("<int:reservation_id>/", views.ReservationRetrieveUpdateAPIView.as_view(), name="reservation-retrieve-update"),
    path("expert/reservations/", views.ExpertReservationListAPIView.as_view(), name="expert-reservation-list"),
    path(
        "expert/reservations/<int:id>/",
        views.ExpertReservationDetailAPIView.as_view(),
        name="expert-reservation-detail",
    ),
    path("schedule/", views.ReservationListForCalendarAPIView.as_view(), name="reservation-list-for-calendar"),
]
