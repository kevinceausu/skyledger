from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Airport, Flight, Booking

User = get_user_model()


class BookingModelTest(TestCase):

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username="testuser",
            password="password",
            role="PASSENGER"
        )

        # Create airports
        self.origin = Airport.objects.create(
            code="DUB",
            name="Dublin Airport",
            city="Dublin",
            country="Ireland"
        )

        self.destination = Airport.objects.create(
            code="LHR",
            name="Heathrow Airport",
            city="London",
            country="UK"
        )

        # Create flight
        self.flight = Flight.objects.create(
            flight_number="SK100",
            origin=self.origin,
            destination=self.destination,
            departure_time="2026-05-01T10:00:00Z",
            arrival_time="2026-05-01T12:00:00Z",
            base_price=Decimal("120.00"),
            capacity=100
        )

    def test_booking_total_price_calculation(self):
        booking = Booking.objects.create(
            booking_reference="TEST001",
            passenger=self.user,
            flight=self.flight,
            seat_class="BUSINESS",
            passenger_count=2
        )

        self.assertEqual(booking.total_price, Decimal("360.00"))