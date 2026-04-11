from django.contrib import admin
from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "passenger",
        "assigned_to",
        "booking",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = (
        "subject",
        "message",
        "passenger__username",
        "assigned_to__username",
        "booking__booking_reference",
    )
