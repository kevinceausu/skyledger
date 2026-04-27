from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from django.shortcuts import render
from flights.models import Flight, Booking
from billing.models import Invoice
from support.models import SupportTicket
from django.contrib.auth import views as auth_views

def home(request):

    context = {}

    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.role in [
            "FLIGHT_MANAGER",
            "BILLING_OFFICER",
            "SUPPORT_AGENT"
        ]:
            context["show_overview"] = True
            context["flight_count"] = Flight.objects.count()
            context["booking_count"] = Booking.objects.count()
            context["invoice_count"] = Invoice.objects.count()
            context["ticket_count"] = SupportTicket.objects.count()
        else:
            context["show_overview"] = False
    else:
        context["show_overview"] = False

    return render(request, "home.html", context)

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('flights/', include('flights.urls')),
    path('billing/', include('billing.urls')),
    path('support/', include('support.urls')),
    path('accounts/', include('accounts.urls')),

    # AUTH
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]