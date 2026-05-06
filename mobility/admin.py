from django.contrib import admin
from .models import Vehicle, PARRecord, ActivityLog

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'make', 'model', 'status', 'latest_odo')
    search_fields = ('plate_number', 'conduction_number', 'chassis_number')
    list_filter = ('status', 'make')

@admin.register(PARRecord)
class PARAdmin(admin.ModelAdmin):
    list_display = ('par_number', 'vehicle', 'issued_to', 'date_issued', 'is_active')
    search_fields = ('par_number', 'issued_to', 'vehicle__plate_number')
    list_filter = ('is_active', 'fund_cluster')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'details')
    readonly_fields = ('timestamp', 'user', 'action', 'details')
    search_fields = ('user__username', 'action', 'details')
    list_filter = ('action', 'timestamp')