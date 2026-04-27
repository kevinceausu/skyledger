from django.shortcuts import render
from .models import Flight, Booking
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from django.shortcuts import redirect
from .forms import AirportForm
from .forms import FlightForm

@login_required
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, "flights/flight_list.html", {"flights": flights})

@login_required
def booking_list(request):

    if request.user.is_superuser:
        bookings = Booking.objects.all()

    elif request.user.role == "PASSENGER":
        bookings = Booking.objects.filter(passenger=request.user)

    elif request.user.role == "FLIGHT_MANAGER":
        bookings = Booking.objects.all()

    else:
        
        bookings = Booking.objects.none()

    bookings = bookings.select_related("passenger", "flight")

    return render(request, "flights/booking_list.html", {"bookings": bookings})

@login_required
def create_booking(request):

    if request.user.role != "PASSENGER":
        return render(request, "403.html")

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.passenger = request.user
            booking.booking_reference = f"BK{Booking.objects.count()+1:03d}"
            booking.save()
            return redirect("/flights/bookings/")
    else:
        form = BookingForm()

    return render(request, "flights/create_booking.html", {"form": form})


@login_required
def create_airport(request):

    if request.user.role != "FLIGHT_MANAGER" and not request.user.is_superuser:
        return render(request, "403.html")

    if request.method == "POST":
        form = AirportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/flights/")
    else:
        form = AirportForm()

    return render(request, "flights/create_airport.html", {"form": form})


@login_required
def create_flight(request):

    if request.user.role != "FLIGHT_MANAGER" and not request.user.is_superuser:
        return render(request, "403.html")

    if request.method == "POST":
        form = FlightForm(request.POST)
        if form.is_valid():
            flight = form.save(commit=False)
            flight.created_by = request.user
            flight.save()
            return redirect("/flights/")
    else:
        form = FlightForm()

    return render(request, "flights/create_flight.html", {"form": form})