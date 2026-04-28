from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehicle, PARRecord, ActivityLog
from .forms import VehicleForm, PARForm
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
import smtplib, ssl
from django.conf import settings

# --- MAIN DASHBOARD & VEHICLE ASSET ADDITION ---
def vehicle_management(request):
    query = Q()
    plate_no = request.GET.get('plate_no')
    if plate_no:
        query &= Q(plate_number__icontains=plate_no) | Q(conduction_number__icontains=plate_no)
    
    all_v = Vehicle.objects.all()
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save()
            ActivityLog.objects.create(
                action_type='CREATE',
                description=f"Added new vehicle: {vehicle.make} {vehicle.model} ({vehicle.plate_number or vehicle.conduction_number})"
            )
            messages.success(request, f"Vehicle added successfully.")
            return redirect('vehicle_management')
    else:
        form = VehicleForm()

    # Context updated to ensure Total Vehicles reflects the entire fleet
    # and all 8 cards in your HTML have corresponding filters.
    context = {
        'vehicles': all_v.filter(query),
        'form': form, 
        'total_vehicles': all_v.count(),  # Reflects every asset regardless of status
        'with_pms': all_v.filter(status='Good Condition').count(),
        'without_pms': all_v.filter(status='No Maintenance Record').count(),
        'for_pms': all_v.filter(status='For PMS').count(),
        'for_registration_renewal': all_v.filter(status='For Registration').count(),
        'for_insurance_renewal': all_v.filter(status='For Insurance').count(),
        'upcoming_repairs': all_v.filter(status='For Repair').count(),
        'upcoming_pms': all_v.filter(status='Upcoming PMS').count(), # Added for your 8th card
    }
    return render(request, 'mobility/vehicle_management.html', context)

# --- DETAILED VEHICLE LIST ---
def vehicle_list_detailed(request):
    """
    Renders the detailed list view of all vehicle assets.
    """
    vehicles = Vehicle.objects.all().order_by('make')
    return render(request, 'mobility/vehicle_list_detailed.html', {'vehicles': vehicles})

# --- PAR MANAGEMENT (ISSUE NEW & REGISTRY TABLE) ---
def par_management(request):
    if request.method == 'POST':
        p_form = PARForm(request.POST)
        if p_form.is_valid():
            par = p_form.save()
            ActivityLog.objects.create(
                action_type='CREATE',
                description=f"Issued PAR {par.par_number} to {par.issued_to}"
            )
            messages.success(request, f"PAR {par.par_number} issued successfully.")
            return redirect('par_management')
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
        action_type='DELETE', 
        description=f"Deleted PAR Record: {par.par_number}"
    )
    par.delete()
    messages.warning(request, "PAR record removed.")
    return redirect('par_management')

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
                action_type='UPDATE',
                description=f"Updated details for {vehicle.plate_number or vehicle.conduction_number}"
            )
            messages.success(request, "Vehicle updated successfully.")
            return redirect('vehicle_management')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'mobility/edit_vehicle.html', {'form': form, 'vehicle': vehicle})

# --- DELETE VEHICLE ---
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    ActivityLog.objects.create(
        action_type='DELETE',
        description=f"Deleted asset: {vehicle.make} ({vehicle.plate_number or vehicle.conduction_number})"
    )
    vehicle.delete()
    messages.warning(request, "Vehicle record deleted.")
    return redirect('vehicle_management')

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
        
    return redirect('vehicle_management')

# --- ACTIVITY LOG ---
def activity_log(request):
    period = request.GET.get('period', 'week')
    days = 7 if period == 'week' else 30
    cutoff = timezone.now() - timedelta(days=days)
    logs = ActivityLog.objects.filter(timestamp__gte=cutoff).order_by('-timestamp')
    return render(request, 'mobility/activity_log.html', {'logs': logs, 'period': period})