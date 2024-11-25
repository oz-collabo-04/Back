from django.urls import path

from common.views import LocationChoicesView, ServiceChoicesView

app_name = "services"
urlpatterns = [
    path("list/", ServiceChoicesView.as_view(), name="list"),
    path("location/list/", LocationChoicesView.as_view(), name="location"),
]
