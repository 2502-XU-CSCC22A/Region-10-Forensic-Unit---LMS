from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection

from .models import Communication, CommunicationPARRecord, CommunicationICSRecord
from .forms import CommunicationPARForm, CommunicationICSForm
from django.contrib.auth.models import User
from mobility.views import Vehicle
from firearms.models import Firearm
from disposal.models import DisposalItem
from config.models import Category, Asset, AssetStatus

def create_activity_log(communication_id, action, details):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO communications_activitylog
            (communication_id, action, details, created_at)
            VALUES (%s, %s, %s, NOW())
            """,
            [communication_id, action, details],
        )


# COMMUNICATIONS LIST
def communications_list(request):
    items = Communication.objects.all()
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.filter(
        asset_ptr__status_id=4 
    )
    current_user_role = request.user.userprofile.role
    
    return render(request, "communications.html", {
        'items': items,
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count(),
        'current_user_role':  current_user_role,
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count(),
        })
    


# ACTIVITY LOGS
def activity_logs(request):
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.filter(asset_ptr__status_id = 4)
    
    current_user_role = request.user.userprofile.role
    
    return render(request, "activity_logs.html", {
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count(),
        'current_user_role':  current_user_role
    })


# PAR MONITORING
def par_monitoring(request):
    pars = (
        CommunicationPARRecord.objects.select_related("communication")
        .all()
        .order_by("-created_at")
    )
    
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.filter(asset_ptr__status_id = 4)
    
    current_user_role = request.user.userprofile.role

    if request.method == "POST":
        p_form = CommunicationPARForm(request.POST)

        if p_form.is_valid():
            par = p_form.save()

            create_activity_log(
                par.communication.asset_ptr_id,
                "Created PAR Record",
                f"PAR {par.par_number} was created for {par.communication.type} issued to {par.issued_to}.",
            )

            return redirect("par_monitoring")

        else:
            print("PAR FORM ERRORS:", p_form.errors)

    else:
        p_form = CommunicationPARForm()

    return render(
        request,
        "par_monitoring.html",
        {
            "p_form": p_form,
            "pars": pars,
            'total_comms': all_c.count() ,
            'total_ber': all_d.count(),
            'total_vehicles': all_v.count(),
            'total_firearms': all_f.count(),
            'current_user_role': current_user_role,
        },
    )


# PRINT PAR
def print_par(request, pk):
    par = get_object_or_404(
        CommunicationPARRecord.objects.select_related("communication"),
        pk=pk
    )

    create_activity_log(
        par.communication.asset_ptr_id,
        "Printed PAR Record",
        f"PAR {par.par_number} for {par.communication.type} was opened for printing.",
    )

    return render(request, "print_par.html", {"par": par})


# EDIT PAR
def edit_par(request, pk):
    record = get_object_or_404(
        CommunicationPARRecord.objects.select_related("communication"),
        pk=pk
    )

    if request.method == "POST":
        form = CommunicationPARForm(request.POST, instance=record)

        if form.is_valid():
            par = form.save()

            create_activity_log(
                par.communication.asset_ptr_id,
                "Updated PAR Record",
                f"PAR {par.par_number} was updated for {par.communication.type}.",
            )

            return redirect("par_monitoring")

        else:
            print("EDIT PAR FORM ERRORS:", form.errors)

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
    record = get_object_or_404(
        CommunicationPARRecord.objects.select_related("communication"),
        pk=pk
    )

    communication_id = record.communication.asset_ptr_id
    par_number = record.par_number
    issued_to = record.issued_to
    asset_type = record.communication.type

    record.delete()

    create_activity_log(
        communication_id,
        "Deleted PAR Record",
        f"PAR {par_number} for {asset_type}, issued to {issued_to}, was deleted from the PAR registry.",
    )

    return redirect("par_monitoring")


# ICS MONITORING
def ics_monitoring(request):
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.filter(asset_ptr__status_id = 4,)
    
    current_user_role = request.user.userprofile.role
    
    icss = (
        CommunicationICSRecord.objects.select_related("communication")
        .all()
        .order_by("-created_at")
    )

    if request.method == "POST":
        i_form = CommunicationICSForm(request.POST)

        if i_form.is_valid():
            ics = i_form.save()

            create_activity_log(
                ics.communication.asset_ptr_id,
                "Created ICS Record",
                f"ICS {ics.ics_number} was created for {ics.communication.type} issued to {ics.issued_to}.",
            )

            return redirect("ics_monitoring")

        else:
            print("ICS FORM ERRORS:", i_form.errors)

    else:
        i_form = CommunicationICSForm()

    return render(
        request,
        "ics_records.html",
        {
            "i_form": i_form,
            "icss": icss,
            'total_comms': all_c.count() ,
            'total_ber': all_d.count(),
            'total_vehicles': all_v.count(),
            'total_firearms': all_f.count(),
            'current_user_role': current_user_role,
        },
    )


# PRINT ICS
def print_ics(request, pk):
    ics = get_object_or_404(
        CommunicationICSRecord.objects.select_related("communication"),
        pk=pk
    )

    create_activity_log(
        ics.communication.asset_ptr_id,
        "Printed ICS Record",
        f"ICS {ics.ics_number} for {ics.communication.type} was opened for printing.",
    )

    return render(request, "print_ics.html", {"ics": ics})


# EDIT ICS
def edit_ics(request, pk):
    record = get_object_or_404(
        CommunicationICSRecord.objects.select_related("communication"),
        pk=pk
    )

    if request.method == "POST":
        form = CommunicationICSForm(request.POST, instance=record)

        if form.is_valid():
            ics = form.save()

            create_activity_log(
                ics.communication.asset_ptr_id,
                "Updated ICS Record",
                f"ICS {ics.ics_number} was updated for {ics.communication.type}.",
            )

            return redirect("ics_monitoring")

        else:
            print("EDIT ICS FORM ERRORS:", form.errors)

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


# DELETE ICS
def delete_ics(request, pk):
    record = get_object_or_404(
        CommunicationICSRecord.objects.select_related("communication"),
        pk=pk
    )

    communication_id = record.communication.asset_ptr_id
    ics_number = record.ics_number
    issued_to = record.issued_to
    asset_type = record.communication.type

    record.delete()

    create_activity_log(
        communication_id,
        "Deleted ICS Record",
        f"ICS {ics_number} for {asset_type}, issued to {issued_to}, was deleted from the ICS registry.",
    )

    return redirect("ics_monitoring")