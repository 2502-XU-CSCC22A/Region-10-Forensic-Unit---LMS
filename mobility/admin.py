from django.contrib import admin
from .models import Vehicle, PARRecord

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # Updated these names to match your new models.py
    list_display = (
        'vehicle_id', 
        'make', 
        'model', 
        'plate_number', 
        'status', 
        'registration_renewal_date', # Added _date
        'insurance_renewal_date'     # Added _date
    )
    search_fields = ('plate_number', 'conduction_number', 'vehicle_id', 'make')
    list_filter = ('status', 'kind')

@admin.register(PARRecord)
class PARAdmin(admin.ModelAdmin):
    list_display = ('par_number', 'vehicle', 'issued_to', 'date_issued')
    search_fields = ('par_number', 'issued_to')