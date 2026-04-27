from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Invoice
from .forms import InvoiceForm
from django.shortcuts import redirect
from datetime import date, timedelta
from flights.models import Booking


@login_required
def invoice_list(request):

    if request.user.is_superuser:
        invoices = Invoice.objects.all()

    elif request.user.role == "PASSENGER":
        invoices = Invoice.objects.filter(passenger=request.user)

    elif request.user.role == "BILLING_OFFICER":
        invoices = Invoice.objects.all()

    else:
        invoices = Invoice.objects.none()

    invoices = invoices.select_related("passenger", "booking")

    return render(request, "billing/invoice_list.html", {"invoices": invoices})


from .forms import InvoiceItemForm

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    
    if request.user.is_superuser:
        pass

    elif request.user.role == "PASSENGER":
        if invoice.passenger != request.user:
            return render(request, "403.html")

    elif request.user.role == "BILLING_OFFICER":
        pass

    else:
        return render(request, "403.html")

    
    if request.method == "POST":
        form = InvoiceItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.invoice = invoice
            item.save()
            return redirect(f"/billing/{invoice.id}/")
    else:
        form = InvoiceItemForm()

    return render(request, "billing/invoice_detail.html", {
        "invoice": invoice,
        "form": form
    })


@login_required
def create_invoice(request):
    if request.user.role != "BILLING_OFFICER" and not request.user.is_superuser:
        return render(request, "403.html")

    used_bookings = Invoice.objects.values_list("booking_id", flat=True)

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        form.fields["booking"].queryset = Booking.objects.exclude(id__in=used_bookings)

        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.passenger = invoice.booking.passenger
            invoice.issued_by = request.user
            invoice.invoice_number = f"INV{Invoice.objects.count() + 1:03d}"
            invoice.status = "ISSUED"
            invoice.save()

            return redirect(f"/billing/{invoice.id}/")
    else:
        form = InvoiceForm()
        form.fields["booking"].queryset = Booking.objects.exclude(id__in=used_bookings)
        form.initial["issue_date"] = date.today()
        form.initial["due_date"] = date.today() + timedelta(days=7)

    return render(request, "billing/create_invoice.html", {"form": form})