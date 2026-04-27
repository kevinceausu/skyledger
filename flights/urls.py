from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path("", views.flight_list, name="flight_list"),
    path("bookings/", views.booking_list, name="booking_list"),

    path("booking/create/", views.create_booking, name="create_booking"),
    path("flight/create/", views.create_flight, name="create_flight"),
    path("airport/create/", views.create_airport, name="create_airport"),
]