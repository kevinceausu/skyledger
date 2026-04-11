from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from flights.models import Booking


class Invoice(models.Model):
    STATUS_DRAFT = "DRAFT"
    STATUS_ISSUED = "ISSUED"
    STATUS_PAID = "PAID"
    STATUS_OVERDUE = "OVERDUE"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ISSUED, "Issued"),
        (STATUS_PAID, "Paid"),
        (STATUS_OVERDUE, "Overdue"),
    ]

    invoice_number = models.CharField(max_length=20, unique=True)
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="invoice"
    )
    passenger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoices"
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_invoices"
    )
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def round_money(self, amount):
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_subtotal(self):
        subtotal = sum((item.line_total for item in self.items.all()), Decimal("0.00"))
        return self.round_money(subtotal)

    def calculate_tax(self):
        tax = self.calculate_subtotal() * Decimal("0.10")
        return self.round_money(tax)

    def calculate_total(self):
        total = self.calculate_subtotal() + self.calculate_tax()
        return self.round_money(total)

    def clean(self):
        if self.due_date < self.issue_date:
            raise ValidationError("Due date cannot be earlier than issue date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def update_totals(self):
        self.subtotal = self.calculate_subtotal()
        self.tax = self.calculate_tax()
        self.total = self.calculate_total()
        super().save(update_fields=["subtotal", "tax", "total"])

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")
        if self.unit_price <= 0:
            raise ValidationError("Unit price must be greater than 0.")

    def save(self, *args, **kwargs):
        self.line_total = Decimal(self.quantity) * self.unit_price
        self.line_total = self.line_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.full_clean()
        super().save(*args, **kwargs)
        self.invoice.update_totals()

    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        invoice.update_totals()

    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"