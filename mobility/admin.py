from django.contrib import admin
from .models import Vehicle, PARRecord, ActivityLog

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # 'asset' displays the linked Property Number from the Config app
    list_display = ('vehicle_id', 'plate_number', 'make', 'model', 'kind', 'status', 'asset')
    search_fields = ('vehicle_id', 'plate_number', 'make', 'model', 'asset__property_no')
    list_filter = ('status', 'kind')

@admin.register(PARRecord)
class PARRecordAdmin(admin.ModelAdmin):
    list_display = ('par_number', 'issued_to', 'vehicle', 'date_issued')
    search_fields = ('par_number', 'issued_to')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'description', 'timestamp')
    list_filter = ('action_type',)
    readonly_fields = ('timestamp',)