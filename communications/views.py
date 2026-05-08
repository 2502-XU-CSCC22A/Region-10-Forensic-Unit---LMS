from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import uuid

from .models import Communication, CommunicationPARRecord, CommunicationICSRecord
from .forms import CommunicationPARForm, CommunicationICSForm

from config.models import Category, Asset


# COMMUNICATIONS LIST
def communications_list(request):
    items = Communication.objects.all()
    return render(request, "communications.html", {"items": items})


# ACTIVITY LOGS
def activity_logs(request):
    return render(request, "activity_logs.html")


# PAR MONITORING
def par_monitoring(request):
    pars = (
        CommunicationPARRecord.objects.select_related("communication")
        .all()
        .order_by("-created_at")
    )

    if request.method == "POST":
        p_form = CommunicationPARForm(request.POST)

        if p_form.is_valid():
            p_form.save()
            return redirect("par_monitoring")
    else:
        p_form = CommunicationPARForm()

    return render(
        request,
        "par_monitoring.html",
        {
            "p_form": p_form,
            "pars": pars,
        },
    )


# PRINT PAR
def print_par(request, pk):
    par = get_object_or_404(
        CommunicationPARRecord.objects.select_related("communication"),
        pk=pk
    )

    return render(request, "print_par.html", {"par": par})


# EDIT PAR
def edit_par(request, pk):
    record = get_object_or_404(CommunicationPARRecord, pk=pk)

    if request.method == "POST":
        form = CommunicationPARForm(request.POST, instance=record)

        if form.is_valid():
            form.save()
            return redirect("par_monitoring")
    else:
        form = CommunicationPARForm(instance=record)

    return render(
        request,
        "edit_par.html",
        {
            "form": form,
            "record": record,
        },
    )


# DELETE PAR
def delete_par(request, pk):
    record = get_object_or_404(CommunicationPARRecord, pk=pk)
    record.delete()

    return redirect("par_monitoring")


# ICS MONITORING
def ics_monitoring(request):
    icss = (
        CommunicationICSRecord.objects.select_related("communication")
        .all()
        .order_by("-created_at")
    )

    if request.method == "POST":
        i_form = CommunicationICSForm(request.POST)

        if i_form.is_valid():
            i_form.save()
            return redirect("ics_monitoring")
    else:
        i_form = CommunicationICSForm()

    return render(
        request,
        "ics_records.html",
        {
            "i_form": i_form,
            "icss": icss,
        },
    )
    
def print_ics(request, pk):
    ics = get_object_or_404(
        CommunicationICSRecord.objects.select_related("communication"),
        pk=pk
    )
    return render(request, "print_ics.html", {"ics": ics})


def edit_ics(request, pk):
    record = get_object_or_404(CommunicationICSRecord, pk=pk)

    if request.method == "POST":
        form = CommunicationICSForm(request.POST, instance=record)

        if form.is_valid():
            form.save()
            return redirect("ics_monitoring")
    else:
        form = CommunicationICSForm(instance=record)

    return render(
        request,
        "edit_ics.html",
        {
            "form": form,
            "record": record,
        },
    )


def delete_ics(request, pk):
    record = get_object_or_404(CommunicationICSRecord, pk=pk)
    record.delete()
    return redirect("ics_monitoring")