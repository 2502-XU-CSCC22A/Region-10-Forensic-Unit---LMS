from django.contrib import admin
from .models import Vehicle, PARRecord, ActivityLog


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):

    list_display = (
        'vehicle_id',
        'plate_number',
        'make_model',
        'classification',
        'primary_driver',
        'status',
        'asset',
        'registration_renewal_date',
        'insurance_renewal_date',
    )

    search_fields = (
        'vehicle_id',
        'plate_number',
        'make_model',
        'primary_driver',
        'alternative_driver',
        'engine_number',
        'chassis_number',
        'asset__property_no',
    )

    list_filter = (
        'status',
        'classification',
        'registration_renewal_date',
        'insurance_renewal_date',
    )

    ordering = ('vehicle_id',)

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    fieldsets = (

        ('Vehicle Information', {
            'fields': (
                'asset',
                'vehicle_id',
                'plate_number',
                'classification',
                'make_model',
                'year',
                'status',
            )
        }),

        ('Driver Assignment', {
            'fields': (
                'primary_driver',
                'alternative_driver',
            )
        }),

        ('Technical Information', {
            'fields': (
                'engine_number',
                'chassis_number',
            )
        }),

        ('Legal / Registration Information', {
            'fields': (
                'conduction_number',
                'registration_renewal_date',
                'insurance_renewal_date',
            )
        }),

        ('System Information', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )


@admin.register(PARRecord)
class PARRecordAdmin(admin.ModelAdmin):

    list_display = (
        'par_number',
        'issued_to',
        'vehicle',
        'date_acquired',
        'expiry_date',
    )

    search_fields = (
        'par_number',
        'issued_to',
        'vehicle__plate_number',
        'vehicle__make_model',
    )

    list_filter = (
        'date_acquired',
        'expiry_date',
    )

    ordering = ('-date_acquired',)

    fieldsets = (

        ('PAR Information', {
            'fields': (
                'vehicle',
                'par_number',
                'issued_to',
            )
        }),

        ('Validity Information', {
            'fields': (
                'date_acquired',
                'expiry_date',
            )
        }),

        ('Additional Notes', {
            'fields': (
                'remarks',
            )
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'action_type',
        'description',
        'timestamp',
    )

    search_fields = (
        'description',
        'user__username',
    )

    list_filter = (
        'action_type',
        'timestamp',
    )

    readonly_fields = (
        'timestamp',
    )

    ordering = ('-timestamp',)