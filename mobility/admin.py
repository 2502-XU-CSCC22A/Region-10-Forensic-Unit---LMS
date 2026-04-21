from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # Added renewal dates to the main list for quick monitoring
    list_display = (
        'vehicle_id', 
        'model', 
        'status', 
        'registration_renewal_date', 
        'insurance_renewal_date'
    )
    
    # Allows you to click 'Available' or 'Maintenance' on the side to filter results
    list_filter = ('status', 'year')
    
    # Added Engine and Chassis number to search so you can find a vehicle by its parts
    search_fields = ('vehicle_id', 'model', 'engine_number', 'chassis_number')
    
    # Makes the list ordered by ID automatically
    ordering = ('vehicle_id',)
    
    # Groups the data into sections when you are editing a vehicle
    fieldsets = (
        ('Basic Information', {
            'fields': ('vehicle_id', 'model', 'year', 'status')
        }),
        ('Technical Details', {
            'fields': ('engine_number', 'chassis_number')
        }),
        ('Compliance & Renewals', {
            'fields': ('registration_renewal_date', 'insurance_renewal_date')
        }),
    )