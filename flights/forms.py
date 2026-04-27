from django import forms
from .models import Booking
from .models import Airport
from .models import Flight



class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["flight", "seat_class", "passenger_count"]

class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = ["code", "name", "city", "country"]






class FlightForm(forms.ModelForm):

    departure_time = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"type": "date"},
            time_attrs={"type": "time"}
        )
    )

    arrival_time = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={"type": "date"},
            time_attrs={"type": "time"}
        )
    )

    class Meta:
        model = Flight
        fields = [
            "flight_number",
            "origin",
            "destination",
            "departure_time",
            "arrival_time",
            "base_price",
            "capacity",
            "status",
        ]

        labels = {
            "departure_time": "Departure (Date & Time)",
            "arrival_time": "Arrival (Date & Time)",
        }