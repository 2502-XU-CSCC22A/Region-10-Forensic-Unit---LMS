from django.shortcuts import render, redirect
from django.utils import timezone
import uuid

# 1. FIX IMPORTS: Point these to your project's folder names
from .models import Communication
from config.models import Category, Asset  # Replace 'config' with the folder where Asset lives

# VIEW 1: Displays the table (Keep this!)
def communications_list(request):
    # Fetch all records from Supabase to show in the table
    items = Communication.objects.all() 
    return render(request, 'communications.html', {'items': items})

# VIEW 2: Saves the new data (The one we fixed)
def add_communication_view(request):
    if request.method == 'POST':
        try:
            # Get data from your modal form
            comm_type = request.POST.get('type')
            imei = request.POST.get('imei_serial')
            freq = request.POST.get('frequency_range')
            stock = request.POST.get('stock_level') or 0

            # Satisfy mandatory Parent (Asset) requirements
            cat = Category.objects.get(category_name="communications")
            unique_id = imei if imei else str(uuid.uuid4())[:8]

            # Create the record in Supabase
            Communication.objects.create(
                type=comm_type,
                imei_serial=imei,
                frequency_range=freq,
                stock_level=stock,
                # Asset fields
                date_acquired=timezone.now().date(),
                model=comm_type or "Unknown",
                property_no=f"PROP-{unique_id}",
                serial_no=f"SN-{unique_id}",
                category=cat
            )
        except Exception as e:
            print(f"ERROR SAVING TO SUPABASE: {e}")
            
    # ALWAYS redirect back to the list so the URL stays clean
    return redirect('communications_list')