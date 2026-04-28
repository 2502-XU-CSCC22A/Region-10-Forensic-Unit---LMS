from django.contrib import admin
from .models import Vehicle, PARRecord, ActivityLog

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_id', 'plate_number', 'make', 'model', 'kind', 'status')
    search_fields = ('vehicle_id', 'plate_number', 'make', 'model')
    list_filter = ('status', 'kind')

@admin.register(PARRecord)
class PARRecordAdmin(admin.ModelAdmin):
    list_display = ('par_number', 'issued_to', 'vehicle', 'date_issued')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'description', 'timestamp')