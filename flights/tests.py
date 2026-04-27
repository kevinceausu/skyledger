from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Airport, Flight, Booking

User = get_user_model()


class BookingModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password",
            role="PASSENGER"
        )

        self.manager = User.objects.create_user(
            username="manager1",
            password="password",
            role="FLIGHT_MANAGER"
        )

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

        self.flight = Flight.objects.create(
            flight_number="SK100",
            origin=self.origin,
            destination=self.destination,
            departure_time="2026-05-01T10:00:00Z",
            arrival_time="2026-05-01T12:00:00Z",
            base_price=Decimal("120.00"),
            capacity=100,
            created_by=self.manager
        )

    # UNIT TEST
    def test_booking_total_price_calculation(self):
        booking = Booking.objects.create(
            booking_reference="TEST001",
            passenger=self.user,
            flight=self.flight,
            seat_class="BUSINESS",
            passenger_count=2
        )

        self.assertEqual(booking.total_price, Decimal("360.00"))

    # INTEGRATION TEST
    def test_passenger_can_create_booking_from_view(self):
        self.client.login(username="testuser", password="password")

        response = self.client.post("/flights/booking/create/", {
            "flight": self.flight.id,
            "seat_class": "ECONOMY",
            "passenger_count": 1,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.count(), 1)

        booking = Booking.objects.first()
        self.assertEqual(booking.passenger, self.user)
        self.assertEqual(booking.total_price, Decimal("120.00"))

    # USE CASE / USER BEHAVIOUR TEST
    def test_flight_manager_can_create_flight_from_view(self):
        self.client.login(username="manager1", password="password")

        response = self.client.post("/flights/flight/create/", {
            "flight_number": "SK999",
            "origin": self.origin.id,
            "destination": self.destination.id,
            "departure_time_0": "2026-06-01",
            "departure_time_1": "10:00:00",
            "arrival_time_0": "2026-06-01",
            "arrival_time_1": "12:00:00",
            "base_price": "150.00",
            "capacity": 180,
            "status": "SCHEDULED",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Flight.objects.filter(flight_number="SK999").exists())