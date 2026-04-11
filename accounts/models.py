from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_PASSENGER = "PASSENGER"
    ROLE_BILLING_OFFICER = "BILLING_OFFICER"
    ROLE_FLIGHT_MANAGER = "FLIGHT_MANAGER"
    ROLE_SUPPORT_AGENT = "SUPPORT_AGENT"

    ROLE_CHOICES = [
        (ROLE_PASSENGER, "Passenger"),
        (ROLE_BILLING_OFFICER, "Billing Officer"),
        (ROLE_FLIGHT_MANAGER, "Flight Manager"),
        (ROLE_SUPPORT_AGENT, "Support Agent"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"