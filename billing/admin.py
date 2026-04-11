from django.contrib import admin
from .models import Invoice, InvoiceItem


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "booking",
        "passenger",
        "issued_by",
        "issue_date",
        "due_date",
        "status",
        "subtotal",
        "tax",
        "total",
    )
    list_filter = ("status", "issue_date", "due_date")
    search_fields = ("invoice_number", "passenger__username", "booking__booking_reference")
    readonly_fields = ("subtotal", "tax", "total")
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "description", "quantity", "unit_price", "line_total")
    readonly_fields = ("line_total",)
    search_fields = ("description", "invoice__invoice_number")