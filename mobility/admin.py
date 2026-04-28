from django.contrib import admin
from .models import Vehicle, PARRecord, ActivityLog, ConfigAsset

@admin.register(ConfigAsset)
class ConfigAssetAdmin(admin.ModelAdmin):
    list_display = ('property_no',)
    search_fields = ('property_no',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # Added 'asset' to display the linked Property Number from Supabase
    list_display = ('vehicle_id', 'plate_number', 'make', 'model', 'kind', 'status', 'asset')
    # You can now search by the linked property number as well
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