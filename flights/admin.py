from django.contrib import admin
from .models import Airport, Flight, Booking


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "city", "country")
    search_fields = ("code", "name", "city", "country")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "flight_number",
        "origin",
        "destination",
        "departure_time",
        "arrival_time",
        "base_price",
        "capacity",
        "status",
    )
    list_filter = ("status", "origin", "destination")
    search_fields = ("flight_number",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_reference",
        "passenger",
        "flight",
        "seat_class",
        "passenger_count",
        "status",
        "total_price",
        "booking_date",
    )
    list_filter = ("status", "seat_class")
    search_fields = ("booking_reference", "passenger__username", "flight__flight_number")