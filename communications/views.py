from django.shortcuts import render, redirect, get_object_or_404
from .models import Communication, CommunicationPARRecord
from .forms import CommunicationPARForm
from django.utils import timezone
import uuid

# IMPORTS
from .models import Communication
from config.models import Category, Asset


# COMMUNICATIONS LIST
def communications_list(request):
    items = Communication.objects.all()

    return render(request, 'communications.html', {
        'items': items
    })


# ACTIVITY LOGS
def activity_logs(request):
    return render(request, 'activity_logs.html')


# PAR MONITORING
def par_monitoring(request):
    pars = CommunicationPARRecord.objects.select_related(
        "communication"
    ).all().order_by("-created_at")

    if request.method == "POST":
        p_form = CommunicationPARForm(request.POST)

        if p_form.is_valid():
            p_form.save()
            return redirect("par_monitoring")

    else:
        p_form = CommunicationPARForm()

    return render(request, "par_monitoring.html", {
        "p_form": p_form,
        "pars": pars,
    })


# PRINT PAR
def print_par(request, pk):
    par = get_object_or_404(
        CommunicationPARRecord.objects.select_related("communication"),
        pk=pk
    )

    return render(request, "print_par.html", {
        "par": par
    })


# EDIT PAR
def edit_par(request, pk):
    record = get_object_or_404(
        CommunicationPARRecord,
        pk=pk
    )

    if request.method == "POST":
        form = CommunicationPARForm(
            request.POST,
            instance=record
        )

        if form.is_valid():
            form.save()
            return redirect("par_monitoring")

    else:
        form = CommunicationPARForm(instance=record)

    return render(request, "edit_par.html", {
        "form": form,
        "record": record,
    })


# DELETE PAR
def delete_par(request, pk):
    record = get_object_or_404(
        CommunicationPARRecord,
        pk=pk
    )

    record.delete()

    return redirect("par_monitoring")