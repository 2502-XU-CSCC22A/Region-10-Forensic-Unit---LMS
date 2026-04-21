from django.shortcuts import render, redirect
from .models import Vehicle
from .forms import VehicleForm
from django.utils import timezone
from datetime import timedelta

def vehicle_management(request):
    # 1. Fetch all records from the database
    vehicles = Vehicle.objects.all()
    today = timezone.now().date()
    upcoming_limit = today + timedelta(days=30)

    # 2. Statistics Calculation (For the 8 Figma Cards)
    total_vehicles = vehicles.count()
    
    # We use 'status' as a proxy for PMS records based on your model fields
    with_pms = vehicles.filter(status='Good').count() 
    without_pms = total_vehicles - with_pms
    
    # Filters based on your prototype requirements
    for_pms = vehicles.filter(status='For PMS').count()
    for_registration_renewal = vehicles.filter(registration_renewal_date__lte=today).count()
    for_insurance_renewal = vehicles.filter(insurance_renewal_date__lte=today).count()
    upcoming_repairs = vehicles.filter(status='Repair Required').count()
    
    # Logic for upcoming maintenance window
    upcoming_pms = vehicles.filter(registration_renewal_date__range=[today, upcoming_limit]).count()

    # 3. Handle the "Add New Vehicle" Form
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicle_management')
    else:
        form = VehicleForm()

    # 4. Consolidate Context for the Template
    context = {
        'vehicles': vehicles,
        'form': form,
        'total_vehicles': total_vehicles,
        'with_pms': with_pms,
        'without_pms': without_pms,
        'for_pms': for_pms,
        'for_registration_renewal': for_registration_renewal,
        'for_insurance_renewal': for_insurance_renewal,
        'upcoming_repairs': upcoming_repairs,
        'upcoming_pms': upcoming_pms,
    }
    
    return render(request, 'mobility/vehicle_management.html', context)