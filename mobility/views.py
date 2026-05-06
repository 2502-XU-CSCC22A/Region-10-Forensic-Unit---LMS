from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

from disposal.models import DisposalItem, DisposalActivityLog
from firearms.models import Firearm
from communications.models import Communication
from .models import Vehicle, PARRecord, ActivityLog
from config.models import AssetStatus 
from .forms import VehicleForm, PARForm

def is_logistics_officer(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'Logistics Officer'

def get_user_role(user):
    return user.userprofile.role if hasattr(user, 'userprofile') else None

@login_required
def vehicle_management(request):
    current_user_role = get_user_role(request.user)
    
    query = Q()
    plate_no = request.GET.get("plate_no")
    if plate_no:
        query &= Q(plate_number__icontains=plate_no) | Q(conduction_number__icontains=plate_no)

    all_v = Vehicle.objects.exclude(status="Disposed")
    total = all_v.count()
    all_d = DisposalItem.objects.all()
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()

    def get_perc(count):
        return (count / total * 100) if total > 0 else 0

    counts = {
        "with_pms": all_v.filter(status="Good Condition").count(),
        "without_pms": all_v.filter(status="No Maintenance Record").count(),
        "for_pms": all_v.filter(status="For PMS").count(),
        "for_registration": all_v.filter(status="For Registration").count(),
        "for_insurance": all_v.filter(status="For Insurance").count(),
        "for_repair": all_v.filter(status="For Repair").count(),
        "upcoming_pms": all_v.filter(status="Upcoming PMS").count(),
    }

    if request.method == "POST":
        if not is_logistics_officer(request.user):
            messages.error(request, "Unauthorized action.")
            return redirect("mobility:vehicle_management")

        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action="CREATE",
                details=f"Added vehicle: {vehicle.make} {vehicle.model} ({vehicle.plate_number or vehicle.conduction_number})"
            )
            messages.success(request, "Vehicle added successfully.")
            return redirect("mobility:vehicle_management")
    else:
        form = VehicleForm()

    context = {
        "form": form,
        "vehicles": all_v.filter(query),
        "total_vehicles": total,
        "current_user_role": current_user_role,
        **counts,
        "p1": get_perc(counts["with_pms"]),
        "p2": get_perc(counts["without_pms"]),
        "p3": get_perc(counts["for_pms"]),
        "p4": get_perc(counts["for_registration"]),
        "p5": get_perc(counts["for_insurance"]),
        "p6": get_perc(counts["for_repair"]),
        "p7": get_perc(counts["upcoming_pms"]),
        'total_disposal':     all_d.count(),
        'total_firearms':     all_f.count(),
        'total_comms':        all_c.count(),
    }
    return render(request, "mobility/vehicle_management.html", context)

@login_required
def vehicle_list_detailed(request):
    current_user_role = get_user_role(request.user)
    vehicles = Vehicle.objects.all().order_by("status", "make")
    return render(request, "mobility/vehicle_list_detailed.html", {
        "vehicles": vehicles,
        "current_user_role": current_user_role
    })

@login_required
def edit_vehicle(request, pk):
    if not is_logistics_officer(request.user):
        messages.error(request, "Permission denied.")
        return redirect("mobility:vehicle_management")

    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action="UPDATE",
                details=f"Updated {vehicle.plate_number or vehicle.conduction_number}"
            )
            messages.success(request, "Vehicle updated.")
            return redirect("mobility:vehicle_management")
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, "mobility/edit_vehicle.html", {"form": form, "vehicle": vehicle})

@login_required
def par_management(request):
    current_user_role = get_user_role(request.user)

    if request.method == "POST":
        if not is_logistics_officer(request.user):
            messages.error(request, "Unauthorized action.")
            return redirect("mobility:par_management")

        p_form = PARForm(request.POST)
        if p_form.is_valid():
            par = p_form.save()
            ActivityLog.objects.create(
                user=request.user,
                action="CREATE",
                details=f"Issued PAR {par.par_number}"
            )
            messages.success(request, f"PAR {par.par_number} issued.")
            return redirect("mobility:par_management")
    else:
        p_form = PARForm()

    context = {
        "pars": PARRecord.objects.filter(is_active=True).order_by("-date_issued"),
        "p_form": p_form,
        "current_user_role": current_user_role,
    }
    return render(request, "mobility/par_management.html", context)

@login_required
def edit_par(request, pk):
    if not is_logistics_officer(request.user):
        messages.error(request, "Permission denied.")
        return redirect("mobility:par_management")

    par = get_object_or_404(PARRecord, pk=pk)
    if request.method == "POST":
        form = PARForm(request.POST, instance=par)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action="UPDATE",
                details=f"Updated PAR record: {par.par_number}"
            )
            messages.success(request, "PAR record updated successfully.")
            return redirect("mobility:par_management")
    else:
        form = PARForm(instance=par)
    
    return render(request, "mobility/par_form.html", {"p_form": form, "par": par})

@login_required
def print_par(request, pk):
    par = get_object_or_404(PARRecord, pk=pk)
    return render(request, 'mobility/print_par.html', {'par': par})

@login_required
def archive_par(request, pk):
    if not is_logistics_officer(request.user):
        messages.error(request, "Permission denied.")
        return redirect("mobility:par_management")

    par = get_object_or_404(PARRecord, pk=pk)
    par.is_active = False
    par.save()

    ActivityLog.objects.create(
        user=request.user,
        action="UPDATE",
        details=f"Archived PAR: {par.par_number}"
    )
    messages.warning(request, f"PAR {par.par_number} archived.")
    return redirect("mobility:par_management")

@login_required
def move_vehicle_to_disposal(request, pk):
    if not is_logistics_officer(request.user):
        messages.error(request, "Permission denied.")
        return redirect("mobility:vehicle_management")

    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == "POST":
        reason = request.POST.get("disposal_reason", "No reason provided")
        
        vehicle.status = "Disposed"
        vehicle.save()

        try:
            disposed_status = AssetStatus.objects.get(status_name='Disposed')
            vehicle.asset.status = disposed_status
            vehicle.asset.save()
        except AssetStatus.DoesNotExist:
            messages.error(request, "Config Error: 'Disposed' status missing.")
            return redirect("mobility:vehicle_management")

        PARRecord.objects.filter(vehicle=vehicle, is_active=True).update(is_active=False)

        ActivityLog.objects.create(
            user=request.user,
            action="DISPOSAL",
            details=f"Vehicle {vehicle.plate_number} decommissioned. Reason: {reason}",
        )

        messages.success(request, f"Vehicle {vehicle.plate_number} moved to disposal.")
        return redirect("mobility:vehicle_management")

    return render(request, "mobility/confirm_disposal.html", {"vehicle": vehicle})

@login_required
def manual_email_alert(request):
    if not is_logistics_officer(request.user):
        return redirect("mobility:vehicle_management")

    m_query = Q(status="For PMS") | Q(status="Upcoming PMS") | Q(status="For Repair")
    flagged = Vehicle.objects.filter(m_query)

    if flagged.exists():
        details = "".join([f"- {v.make} ({v.plate_number or v.conduction_number}) | Status: {v.status}\n" for v in flagged])
        
        try:
            send_mail(
                "Maintenance Alert - RFU 10",
                f"Required maintenance:\n\n{details}",
                settings.DEFAULT_FROM_EMAIL,
                ['admin@rfu10.pnp.gov.ph'],
                fail_silently=False,
            )
            messages.success(request, "Alerts sent.")
        except Exception:
            messages.error(request, "Mail delivery failed.")
    
    return redirect("mobility:vehicle_management")

@login_required
def activity_log(request):
    current_user_role = get_user_role(request.user)
    period = request.GET.get("period", "week")
    days = 7 if period == "week" else 30
    cutoff = timezone.now() - timedelta(days=days)

    logs = ActivityLog.objects.filter(timestamp__gte=cutoff).select_related("user").order_by("-timestamp")

    return render(request, "mobility/activity_log.html", {
        "logs": logs,
        "period": period,
        "current_user_role": current_user_role
    })