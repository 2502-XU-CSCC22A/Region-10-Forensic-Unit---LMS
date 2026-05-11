from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from config.models import Asset


class ConfigAsset(models.Model):

    class Meta:
        managed = False
        db_table = 'config_asset'

    property_no = models.CharField(max_length=100)

    def __str__(self):
        return self.property_no


class Vehicle(models.Model):

    STATUS_CHOICES = [
        ('Serviceable', 'Serviceable'),
        ('Unserviceable', 'Unserviceable'),
        ('BER', 'BER'),
        ('Disposed', 'Disposed'),
    ]

    CLASSIFICATION_CHOICES = [
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Pick-up', 'Pick-up'),
        ('Van', 'Van'),
        ('Motorcycle', 'Motorcycle'),
        ('Multi-Cab', 'Multi-Cab'),
        ('Utility Vehicle', 'Utility Vehicle'),
        ('Mobile Laboratory', 'Mobile Laboratory'),
        ('Service Vehicle', 'Service Vehicle'),
        ('Patrol Vehicle', 'Patrol Vehicle'),
        ('Transport Vehicle', 'Transport Vehicle'),
        ('Rescue Vehicle', 'Rescue Vehicle'),
        ('Tactical Vehicle', 'Tactical Vehicle'),
    ]

    asset = models.ForeignKey(
        Asset,
        db_column='asset_id',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicle_details'
    )

    vehicle_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    plate_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    primary_driver = models.CharField(max_length=100, null=True, blank=True)
    alternative_driver = models.CharField(max_length=100, null=True, blank=True)

    classification = models.CharField(
        max_length=50,
        choices=CLASSIFICATION_CHOICES,
        null=True,
        blank=True
    )

    make_model = models.CharField(max_length=100)
    year = models.CharField(max_length=4, null=True, blank=True)
    conduction_number = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Serviceable'
    )

    engine_number = models.CharField(max_length=100, null=True, blank=True)
    chassis_number = models.CharField(max_length=100, null=True, blank=True)
    registration_renewal_date = models.DateField(null=True, blank=True)
    insurance_renewal_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make_model} ({self.plate_number or self.conduction_number})"

    def save(self, *args, **kwargs):
        old_status = None

        if self.pk:
            old_vehicle = Vehicle.objects.filter(pk=self.pk).first()
            if old_vehicle:
                old_status = old_vehicle.status

        if not self.asset:
            asset_property_no = (
                self.vehicle_id
                or self.plate_number
                or self.conduction_number
            )

            if asset_property_no:
                asset, created = Asset.objects.get_or_create(
                    property_no=asset_property_no,
                    defaults={
                        'StatusID_id': 1,
                        'category_id': 10,
                        'quantity': 1,
                    }
                )

                self.asset = asset

        super().save(*args, **kwargs)

        if self.status == 'BER' and old_status != 'BER' and self.asset:
            from disposal.models import DisposalItem, DisposalActivityLog

            DisposalItem.objects.get_or_create(
                property_no=self.asset.property_no,
                defaults={
                    'disposal_reason': 'Vehicle marked as BER from Mobility Branch.',
                    'processed_by': None,
                    'expiry_date': self.registration_renewal_date,
                }
            )

            DisposalActivityLog.objects.create(
                asset=self.asset,
                action_type='FLAGGED',
                description=f"Vehicle {self.plate_number or self.conduction_number} flagged as BER from Mobility Branch.",
                disposal_reason='Vehicle marked as BER from Mobility Branch.'
            )


class PARRecord(models.Model):

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='par_records'
    )

    par_number = models.CharField(max_length=50, unique=True)
    issued_to = models.CharField(max_length=100)

    date_acquired = models.DateField(
        default=timezone.now,
        db_column='date_acquired'
    )

    expiry_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.par_number} - {self.issued_to}"

    class Meta:
        verbose_name = "PAR Record"
        verbose_name_plural = "PAR Records"
        ordering = ['-date_acquired']


class ActivityLog(models.Model):

    ACTION_CHOICES = [
        ('INFO', 'Info'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action_type = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        default='INFO'
    )

    description = models.TextField(default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_action_type_display(self):
        return self.action_type.capitalize()