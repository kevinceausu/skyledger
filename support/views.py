from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import SupportTicket
from .forms import SupportTicketForm
from django.shortcuts import redirect


@login_required
def support_list(request):

    if request.user.is_superuser:
        tickets = SupportTicket.objects.all()

    elif request.user.role == "PASSENGER":
        tickets = SupportTicket.objects.filter(passenger=request.user)

    elif request.user.role == "SUPPORT_AGENT":
        tickets = SupportTicket.objects.filter(assigned_to=request.user)

    else:
        tickets = SupportTicket.objects.none()

    tickets = tickets.select_related("passenger", "assigned_to", "booking")

    return render(request, "support/support_list.html", {"tickets": tickets})


@login_required
def support_detail(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)

    if request.user.is_superuser:
        return render(request, "support/support_detail.html", {"ticket": ticket})

    if request.user.role == "PASSENGER" and ticket.passenger != request.user:
        return render(request, "403.html")

    if request.user.role == "SUPPORT_AGENT" and ticket.assigned_to != request.user:
        return render(request, "403.html")

    if request.user.role not in ["PASSENGER", "SUPPORT_AGENT"]:
        return render(request, "403.html")

    return render(request, "support/support_detail.html", {"ticket": ticket})


@login_required
def create_ticket(request):

    if request.user.role != "PASSENGER":
        return render(request, "403.html")

    if request.method == "POST":
        form = SupportTicketForm(request.POST)

       
        form.fields["booking"].queryset = request.user.bookings.all()

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.passenger = request.user
            ticket.status = "OPEN"
            ticket.save()
            return redirect("/support/")
    else:
        form = SupportTicketForm()

    
        form.fields["booking"].queryset = request.user.bookings.all()

    return render(request, "support/create_ticket.html", {"form": form})