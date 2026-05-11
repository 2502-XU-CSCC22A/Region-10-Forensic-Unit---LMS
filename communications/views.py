from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from .models import Communication, CommunicationPARRecord
from .forms import CommunicationPARForm
from django.contrib.auth.models import User
from mobility.views import Vehicle
from firearms.models import Firearm
from disposal.models import DisposalItem
from django.utils import timezone
import uuid
from .models import Communication, CommunicationPARRecord, CommunicationICSRecord
from .forms import CommunicationPARForm, CommunicationICSForm

from config.models import Category, Asset, AssetStatus
from .models import Communication

def create_activity_log(communication_id, action, details):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO communications_activitylog
            (communication_id, action, details, created_at)
            VALUES (%s, %s, %s, NOW())
        """, [communication_id, action, details])

# COMMUNICATIONS LIST
def communications_list(request):
    # Fetch all records from Supabase to show in the table
    items = Communication.objects.all() 
    
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
    ).count()
        
    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None
        
    return render(request, 'communications/communications.html', {
        'items': items,
        'total_comms': all_c.count() ,
        'total_ber': all_d,
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count(),
        'current_user_role':  current_user_role
        })

def par_monitoring(request):
    return render(request, 'communications/par_monitoring.html')

# ACTIVITY LOGS
def activity_logs(request):
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.all()
    
    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None
        
    return render(request, 'communications/activity_logs.html',  {
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count(),
        'current_user_role':  current_user_role
    })

# PAR MONITORING
def par_monitoring(request):
    pars = CommunicationPARRecord.objects.select_related("communication").all().order_by("-created_at")

    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.all()
    
    current_user_role = request.user.userprofile.role
    
    if request.method == "POST":
        p_form = CommunicationPARForm(request.POST)

        if p_form.is_valid():
            par = p_form.save()

            create_activity_log(
                par.communication.asset_ptr_id,
                "Created PAR Record",
                f"PAR {par.par_number} was created for {par.communication.type} issued to {par.issued_to}."
            )

            return redirect("par_monitoring")
    else:
        p_form = CommunicationPARForm()

    return render(request, "communications/par_monitoring.html", {
        "p_form": p_form,
        "pars": pars,
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count(),
        'current_user_role': current_user_role,
    })
    
def print_par(request, pk):
    par = get_object_or_404(
        CommunicationPARRecord.objects.select_related("communication"),
        pk=pk
    )

    create_activity_log(
        par.communication.asset_ptr_id,
        "Printed PAR Record",
        f"PAR {par.par_number} for {par.communication.type} was opened for printing."
    )

    return render(request, "communications/print_par.html", {"par": par})


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
                f"PAR {par.par_number} was updated for {par.communication.type}."
            )

            return redirect("par_monitoring")
    else:
        form = CommunicationPARForm(instance=record)

    return render(
        request,
        "communications/edit_par.html",
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
        f"PAR {par_number} for {asset_type}, issued to {issued_to}, was deleted from the PAR registry."
    )

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
        "communications/ics_records.html",
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
    return render(request, "communications/print_ics.html", {"ics": ics})


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
        "communications/edit_ics.html",
        {
            "form": form,
            "record": record,
        },
    )

def delete_ics(request, pk):
    record = get_object_or_404(CommunicationICSRecord, pk=pk)
    record.delete()
    return redirect("ics_monitoring")