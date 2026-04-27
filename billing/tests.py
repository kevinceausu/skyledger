from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from flights.models import Airport, Flight, Booking
from .models import Invoice, InvoiceItem

User = get_user_model()


class InvoiceModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            password="password",
            role="PASSENGER"
        )

        self.staff = User.objects.create_user(
            username="billing1",
            password="password",
            role="BILLING_OFFICER"
        )

        origin = Airport.objects.create(
            code="DUB",
            name="Dublin",
            city="Dublin",
            country="Ireland"
        )

        dest = Airport.objects.create(
            code="LHR",
            name="London",
            city="London",
            country="UK"
        )

        self.flight = Flight.objects.create(
            flight_number="SK200",
            origin=origin,
            destination=dest,
            departure_time="2026-05-01T10:00:00Z",
            arrival_time="2026-05-01T12:00:00Z",
            base_price=Decimal("120.00"),
            capacity=100
        )

        self.booking = Booking.objects.create(
            booking_reference="BKTEST",
            passenger=self.user,
            flight=self.flight,
            seat_class="BUSINESS",
            passenger_count=2
        )

        self.invoice = Invoice.objects.create(
            invoice_number="INVTEST",
            booking=self.booking,
            passenger=self.user,
            issued_by=self.staff,
            issue_date="2026-05-01",
            due_date="2026-05-10"
        )

    # UNIT TEST
    def test_invoice_totals(self):
        InvoiceItem.objects.create(
            invoice=self.invoice,
            description="Flight Fare",
            quantity=2,
            unit_price=Decimal("180.00")
        )

        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.subtotal, Decimal("360.00"))
        self.assertEqual(self.invoice.tax, Decimal("36.00"))
        self.assertEqual(self.invoice.total, Decimal("396.00"))

    # INTEGRATION TEST
    def test_billing_officer_can_create_invoice(self):
        second_booking = Booking.objects.create(
            booking_reference="BKNEW",
            passenger=self.user,
            flight=self.flight,
            seat_class="ECONOMY",
            passenger_count=1
        )

        self.client.login(username="billing1", password="password")

        response = self.client.post("/billing/create/", {
            "booking": second_booking.id,
            "issue_date": "2026-05-01",
            "due_date": "2026-05-10",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Invoice.objects.filter(booking=second_booking).exists())

    # USE CASE / USER BEHAVIOUR TEST
    def test_billing_officer_can_add_invoice_item(self):
        self.client.login(username="billing1", password="password")

        response = self.client.post(f"/billing/{self.invoice.id}/", {
            "description": "Extra Baggage",
            "quantity": 1,
            "unit_price": "50.00",
        })

        self.assertEqual(response.status_code, 302)

        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.subtotal, Decimal("50.00"))
        self.assertEqual(self.invoice.tax, Decimal("5.00"))
        self.assertEqual(self.invoice.total, Decimal("55.00"))