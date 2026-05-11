from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehicle, PARRecord, ActivityLog
from .forms import VehicleForm
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
import smtplib
import ssl
from django.conf import settings
from disposal.models import DisposalItem
from firearms.models import Firearm
from communications.models import Communication
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


# =========================================================
# ROLE CHECK
# =========================================================

def can_edit(user):
    try:
        role = user.userprofile.role
        return role in ['Admin', 'Logistics Officer']
    except Exception:
        return False


# =========================================================
# MAIN DASHBOARD & VEHICLE MANAGEMENT
# =========================================================

@login_required
def vehicle_management(request):
    query = Q()
    search = request.GET.get('plate_no')

    if search:
        query &= (
            Q(vehicle_id__icontains=search) |
            Q(plate_number__icontains=search) |
            Q(conduction_number__icontains=search) |
            Q(make_model__icontains=search) |
            Q(classification__icontains=search) |
            Q(primary_driver__icontains=search) |
            Q(alternative_driver__icontains=search)
        )

    all_d = DisposalItem.objects.all()
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()

    if request.method == 'POST':
        if not can_edit(request.user):
            return HttpResponseForbidden("You do not have permission.")

        form = VehicleForm(request.POST)

        if form.is_valid():
            vehicle = form.save()

            par_number = form.cleaned_data.get('par_number')
            issued_to = form.cleaned_data.get('issued_to')
            date_acquired = form.cleaned_data.get('date_acquired')
            expiry_date = form.cleaned_data.get('expiry_date')
            remarks = form.cleaned_data.get('remarks')

            if par_number and issued_to:
                PARRecord.objects.create(
                    vehicle=vehicle,
                    par_number=par_number,
                    issued_to=issued_to,
                    date_acquired=date_acquired,
                    expiry_date=expiry_date,
                    remarks=remarks
                )

            ActivityLog.objects.create(
                user=request.user,
                action_type='CREATE',
                description=f"Added new vehicle: {vehicle.make_model} ({vehicle.plate_number or vehicle.conduction_number})"
            )

            messages.success(request, "Vehicle and PAR details added successfully.")
            return redirect('mobility:vehicle_management')
    else:
        form = VehicleForm()

    all_v = Vehicle.objects.all()

    total_vehicles = all_v.count()
    s_count = all_v.filter(status='Serviceable').count()
    u_count = all_v.filter(status='Unserviceable').count()
    ber_count = all_v.filter(status='BER').count()

    today = timezone.now().date()
    upcoming_limit = today + timedelta(days=30)

    expiring_count = PARRecord.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=upcoming_limit
    ).count()

    context = {
        'form': form,
        'vehicles': all_v.filter(query).order_by('-id'),
        'can_edit': can_edit(request.user),

        'total_vehicles': total_vehicles,
        's_count': s_count,
        'u_count': u_count,
        'ber_count': ber_count,
        'expiring_count': expiring_count,

        'total_disposal': all_d.count(),
        'total_firearms': all_f.count(),
        'total_comms': all_c.count(),
    }

    return render(request, 'mobility/vehicle_management.html', context)


# =========================================================
# EDIT VEHICLE
# =========================================================

@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if vehicle.status == 'Disposed':
        messages.error(request, "Disposed vehicles are locked from editing.")
        return redirect('mobility:vehicle_management')

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)

        if form.is_valid():
            updated_vehicle = form.save()

            ActivityLog.objects.create(
                user=request.user,
                action_type='UPDATE',
                description=f"Updated vehicle: {updated_vehicle.make_model} ({updated_vehicle.plate_number or updated_vehicle.conduction_number})"
            )

            messages.success(request, "Vehicle updated successfully.")
            return redirect('mobility:vehicle_management')

    return redirect('mobility:vehicle_management')


# =========================================================
# DELETE VEHICLE
# =========================================================

@login_required
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if vehicle.status == 'Disposed':
        messages.error(request, "Disposed vehicles cannot be deleted.")
        return redirect('mobility:vehicle_management')

    ActivityLog.objects.create(
        user=request.user,
        action_type='DELETE',
        description=f"Deleted vehicle: {vehicle.make_model} ({vehicle.plate_number or vehicle.conduction_number})"
    )

    vehicle.delete()
    messages.warning(request, "Vehicle record deleted.")
    return redirect('mobility:vehicle_management')


# =========================================================
# MARK VEHICLE AS BER
# =========================================================

@login_required
def mark_vehicle_ber(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if vehicle.status != 'Disposed':
        vehicle.status = 'BER'
        vehicle.save()

        ActivityLog.objects.create(
            user=request.user,
            action_type='UPDATE',
            description=f"Marked vehicle as BER: {vehicle.make_model} ({vehicle.plate_number or vehicle.conduction_number})"
        )

        messages.warning(request, "Vehicle marked as BER and reflected in Disposal/BER.")

    return redirect('mobility:vehicle_management')


# =========================================================
# SEND BER VEHICLE TO DISPOSAL
# =========================================================

@login_required
def send_vehicle_to_disposal(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if vehicle.status == 'BER':
        vehicle.status = 'Disposed'
        vehicle.save()

        ActivityLog.objects.create(
            user=request.user,
            action_type='UPDATE',
            description=f"Vehicle disposed via BER Department: {vehicle.make_model} ({vehicle.plate_number or vehicle.conduction_number})"
        )

        messages.success(request, "Vehicle has been marked as disposed.")

    return redirect('mobility:vehicle_management')


# =========================================================
# PAR MONITORING
# =========================================================

@login_required
def par_management(request):
    today = timezone.now().date()
    upcoming_limit = today + timedelta(days=30)

    search = request.GET.get('search')
    status = request.GET.get('status')

    pars = PARRecord.objects.select_related('vehicle').all()

    if search:
        pars = pars.filter(
            Q(par_number__icontains=search) |
            Q(issued_to__icontains=search) |
            Q(vehicle__vehicle_id__icontains=search) |
            Q(vehicle__plate_number__icontains=search) |
            Q(vehicle__conduction_number__icontains=search) |
            Q(vehicle__make_model__icontains=search)
        )

    if status == 'expiring':
        pars = pars.filter(
            expiry_date__gte=today,
            expiry_date__lte=upcoming_limit
        )
    elif status == 'expired':
        pars = pars.filter(expiry_date__lt=today)
    elif status == 'active':
        pars = pars.filter(expiry_date__gt=upcoming_limit)

    context = {
        'pars': pars.order_by('-date_acquired'),
        'today': today,
        'upcoming_limit': upcoming_limit,
        'search': search,
        'status': status,
    }

    return render(request, 'mobility/par_management.html', context)


# =========================================================
# DELETE PAR
# =========================================================

@login_required
def delete_par(request, pk):
    par = get_object_or_404(PARRecord, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    ActivityLog.objects.create(
        user=request.user,
        action_type='DELETE',
        description=f"Deleted PAR Record: {par.par_number}"
    )

    par.delete()
    messages.warning(request, "PAR record removed.")
    return redirect('mobility:par_management')


# =========================================================
# PRINT PAR
# =========================================================

@login_required
def print_par(request, pk):
    par = get_object_or_404(
        PARRecord.objects.select_related('vehicle'),
        pk=pk
    )

    return render(request, 'mobility/print_par.html', {'par': par})


# =========================================================
# ACTIVITY LOG
# =========================================================

@login_required
def activity_log(request):
    period = request.GET.get('period', 'week')
    days = 7 if period == 'week' else 30
    cutoff = timezone.now() - timedelta(days=days)

    logs = ActivityLog.objects.filter(
        timestamp__gte=cutoff
    ).select_related('user').order_by('-timestamp')

    return render(request, 'mobility/activity_log.html', {
        'logs': logs,
        'period': period
    })


# =========================================================
# EMAIL ALERT SYSTEM
# =========================================================

@login_required
def manual_email_alert(request):
    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    urgent = Vehicle.objects.filter(status__in=['Unserviceable', 'BER'])

    if urgent.exists():
        vehicle_list = "\n".join([
            f"- {v.make_model} ({v.plate_number or v.conduction_number}): {v.status}"
            for v in urgent
        ])

        message_body = (
            "Subject: RFU 10 Mobility Alert\n\n"
            "The following vehicles require immediate attention:\n\n"
            f"{vehicle_list}\n\n"
            "Please update the records once action has been taken."
        )

        try:
            context = ssl._create_unverified_context()

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls(context=context)
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(
                    settings.EMAIL_HOST_USER,
                    ['dlpalayen@gmail.com'],
                    message_body
                )

            messages.success(request, "Alert email sent successfully!")

        except Exception as e:
            messages.error(request, f"Email failed: {e}")

    else:
        messages.info(request, "No urgent vehicle records found.")

    return redirect('mobility:vehicle_management')