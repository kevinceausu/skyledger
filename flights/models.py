from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.city}"


class Flight(models.Model):
    STATUS_SCHEDULED = "SCHEDULED"
    STATUS_DELAYED = "DELAYED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_DELAYED, "Delayed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_COMPLETED, "Completed"),
    ]

    flight_number = models.CharField(max_length=10, unique=True)
    origin = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_flights"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_flights"
    )

    def clean(self):
        if self.origin == self.destination:
            raise ValidationError("Origin and destination cannot be the same airport.")
        if self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival time must be after departure time.")
        if self.base_price <= 0:
            raise ValidationError("Base price must be greater than 0.")
        if self.capacity <= 0:
            raise ValidationError("Capacity must be greater than 0.")

    def __str__(self):
        return self.flight_number


class Booking(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    CLASS_ECONOMY = "ECONOMY"
    CLASS_BUSINESS = "BUSINESS"
    CLASS_FIRST = "FIRST"

    CLASS_CHOICES = [
        (CLASS_ECONOMY, "Economy"),
        (CLASS_BUSINESS, "Business"),
        (CLASS_FIRST, "First"),
    ]

    booking_reference = models.CharField(max_length=20, unique=True)
    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    seat_class = models.CharField(
        max_length=20,
        choices=CLASS_CHOICES,
        default=CLASS_ECONOMY
    )
    passenger_count = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def get_class_multiplier(self):
        multipliers = {
            self.CLASS_ECONOMY: Decimal("1.00"),
            self.CLASS_BUSINESS: Decimal("1.50"),
            self.CLASS_FIRST: Decimal("2.00"),
        }
        return multipliers.get(self.seat_class, Decimal("1.00"))

    def calculate_total_price(self):
        base = self.flight.base_price
        multiplier = self.get_class_multiplier()
        total = base * multiplier * self.passenger_count
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def clean(self):
        if self.passenger_count <= 0:
            raise ValidationError("Passenger count must be greater than 0.")

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.booking_reference