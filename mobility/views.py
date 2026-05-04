from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehicle, PARRecord, ActivityLog
from .forms import VehicleForm, PARForm
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
import smtplib, ssl
from django.conf import settings
from disposal.models import DisposalItem, DisposalActivityLog
from firearms.models import Firearm
from communications.models import Communication
from django.contrib.auth.decorators import login_required

@login_required
def edit_vehicle(request, pk):
    # ... your existing code ...
    if request.method == 'POST':
        if form.is_valid():
            vehicle = form.save()
            ActivityLog.objects.create(
                user=request.user,  # This will now always be a valid User
                action_type='UPDATE',
                description=f'Updated details for {vehicle.plate_number}'
            )


# --- MAIN DASHBOARD & VEHICLE ASSET ADDITION ---
def vehicle_management(request):
    query = Q()
    plate_no = request.GET.get('plate_no')
    if plate_no:
        query &= Q(plate_number__icontains=plate_no) | Q(conduction_number__icontains=plate_no)
    
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.all()
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action_type='CREATE',
                description=f"Added new vehicle: {vehicle.make} {vehicle.model} ({vehicle.plate_number or vehicle.conduction_number})"
            )
            messages.success(request, f"Vehicle added successfully.")
            return redirect('mobility:vehicle_management')
    else:
        form = VehicleForm()

    all_v = Vehicle.objects.all()
    total = all_v.count()
    
    with_pms_count = all_v.filter(status='Good Condition').count()
    without_pms_count = all_v.filter(status='No Maintenance Record').count()
    for_pms_count = all_v.filter(status='For PMS').count()
    for_reg_count = all_v.filter(status='For Registration').count()
    for_ins_count = all_v.filter(status='For Insurance').count()
    up_repairs_count = all_v.filter(status='For Repair').count()
    up_pms_count = all_v.filter(status='Upcoming PMS').count()

    def get_perc(count):
        return (count / total * 100) if total > 0 else 0

    context = {
        'form': form, 
        'vehicles': all_v.filter(query),
        'form': form, 
        'total_vehicles': total,
        'with_pms': with_pms_count,
        'without_pms': without_pms_count,
        'for_pms': for_pms_count,
        'for_registration_renewal': for_reg_count,
        'for_insurance_renewal': for_ins_count,
        'upcoming_repairs': up_repairs_count,
        'upcoming_pms': up_pms_count,
        'p1': get_perc(with_pms_count),
        'p2': get_perc(without_pms_count),
        'p3': get_perc(for_pms_count),
        'p4': get_perc(for_reg_count),
        'p5': get_perc(for_ins_count),
        'p6': get_perc(up_repairs_count),
        'p7': get_perc(up_pms_count),
        'total_disposal':     all_d.count(),
        'total_firearms':     all_f.count(),
        'total_comms':        all_c.count(),
    }
    return render(request, 'mobility/vehicle_management.html', context)

# --- DETAILED VEHICLE LIST ---
def vehicle_list_detailed(request):
    vehicles = Vehicle.objects.all().order_by('make')
    return render(request, 'mobility/vehicle_list_detailed.html', {'vehicles': vehicles})

# --- PAR MANAGEMENT (ISSUE NEW & REGISTRY TABLE) ---
def par_management(request):
    if request.method == 'POST':
        p_form = PARForm(request.POST)
        if p_form.is_valid():
            par = p_form.save()
            ActivityLog.objects.create(
                user=request.user,
                action_type='CREATE',
                description=f"Issued PAR {par.par_number} to {par.issued_to}"
            )
            messages.success(request, f"PAR {par.par_number} issued successfully.")
            return redirect('mobility:par_management')
    else:
        p_form = PARForm()
    
    context = {
        'pars': PARRecord.objects.all().order_by('-date_issued'),
        'p_form': p_form, 
    }
    return render(request, 'mobility/par_management.html', context)

# --- EDIT PAR RECORD ---
def edit_par(request, pk):
    record = get_object_or_404(PARRecord, pk=pk)
    if request.method == 'POST':
        form = PARForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action_type='UPDATE',
                description=f"Updated PAR Record: {record.par_number}"
            )
            messages.success(request, "PAR Record updated successfully.")
            return redirect('par_management')
    else:
        form = PARForm(instance=record)
    
    return render(request, 'mobility/edit_par.html', {'form': form, 'record': record})

# --- DELETE PAR RECORD ---
def delete_par(request, pk):
    par = get_object_or_404(PARRecord, pk=pk)
    ActivityLog.objects.create(
        user=request.user,
        action_type='DELETE', 
        description=f"Deleted PAR Record: {par.par_number}"
    )
    par.delete()
    messages.warning(request, "PAR record removed.")
    return redirect('mobility:par_management')

# --- PRINT PAR ---
def print_par(request, pk):
    par = get_object_or_404(PARRecord, pk=pk)
    return render(request, 'mobility/print_par.html', {'par': par})

# --- EDIT VEHICLE ---
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action_type='UPDATE',
                description=f"Updated details for {vehicle.plate_number or vehicle.conduction_number}"
            )
            messages.success(request, "Vehicle updated successfully.")
            return redirect('mobility:vehicle_management')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'mobility/edit_vehicle.html', {'form': form, 'vehicle': vehicle})

# --- DELETE VEHICLE ---
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    ActivityLog.objects.create(
        user=request.user,
        action_type='DELETE',
        description=f"Deleted asset: {vehicle.make} ({vehicle.plate_number or vehicle.conduction_number})"
    )
    vehicle.delete()
    messages.warning(request, "Vehicle record deleted.")
    return redirect('mobility:vehicle_management')

# --- EMAIL ALERT SYSTEM ---
def manual_email_alert(request):
    urgent = Vehicle.objects.filter(status__in=['For Repair', 'For PMS', 'For Registration'])
    
    if urgent.exists():
        vehicle_list = "\n".join([f"- {v.make} {v.model} ({v.plate_number or v.conduction_number}): {v.status}" for v in urgent])
        message_body = (
            f"Subject: RFU 10 Mobility Alert: Maintenance Required\n\n"
            f"Good day,\n\nThis is an automated alert from the RFU 10 Logistics Management System.\n\n"
            f"The following vehicles require maintenance or administrative action:\n\n{vehicle_list}\n\n"
            f"Please update the system records once actions are taken."
        )
        
        try:
            context = ssl._create_unverified_context()
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls(context=context)
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(settings.EMAIL_HOST_USER, ['dlpalayen@gmail.com'], message_body)
                
            messages.success(request, "Alert emails sent successfully!")
        except Exception as e:
            messages.error(request, f"Email failed: {e}")
    else:
        messages.info(request, "No urgent records found.")
        
    return redirect('mobility:vehicle_management')

# --- ACTIVITY LOG ---
def activity_log(request):
    period = request.GET.get('period', 'week')
    days = 7 if period == 'week' else 30
    cutoff = timezone.now() - timedelta(days=days)
    logs = ActivityLog.objects.filter(timestamp__gte=cutoff).select_related('user').order_by('-timestamp')
    user=request.user,
    return render(request, 'mobility/activity_log.html', {'logs': logs, 'period': period, 'user': user})

def move_vehicle_to_disposal(request, pk):
    # 1. Get the vehicle and its associated asset
    vehicle = get_object_or_404(Vehicle, pk=pk)
    asset_instance = vehicle.asset 

    if request.method == 'POST':
        reason = request.POST.get('disposal_reason', 'No reason provided')
        
        # 2. Create the DisposalItem
        # Since DisposalItem inherits from Asset, we link it to the existing property_no
        disposal_entry = DisposalItem.objects.create(
            # Copying data from the existing asset/vehicle
            property_no=asset_instance.property_no, 
            disposal_reason=reason,
            processed_by=request.user,
            # If your Vehicle has an expiry/renewal date, map it here
            expiry_date=vehicle.registration_renewal_date 
        )

        # 3. Update Vehicle Status to 'Disposed'
        vehicle.status = 'Disposed'
        vehicle.save()

        # 4. Log the activity in BOTH logs for a complete audit trail
        # Mobility Log
        ActivityLog.objects.create(
            user=request.user,
            action_type='UPDATE',
            description=f"Vehicle {vehicle.plate_number} moved to Disposal Registry."
        )
        
        # Disposal Log
        DisposalActivityLog.objects.create(
            user=request.user,
            asset=asset_instance,
            action_type='CREATE',
            description=f"Vehicle {vehicle.plate_number} flagged for disposal.",
            disposal_reason=reason
        )

        messages.success(request, f"Vehicle {vehicle.plate_number} successfully moved to disposal.")
        return redirect('mobility:vehicle_management')

    return render(request, 'mobility/confirm_disposal.html', {'vehicle': vehicle})