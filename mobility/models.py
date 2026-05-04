from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from config.models import Asset

class ConfigAsset(models.Model):
    class Meta:
        managed = False  # Django will not try to modify this table
        db_table = 'config_asset'
    
    property_no = models.CharField(max_length=100)

    def __str__(self):
        return self.property_no

class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('Good Condition', 'Good Condition'),
        ('For Registration', 'For Registration'),
        ('For Insurance', 'For Insurance'),
        ('For PMS', 'For PMS'),
        ('For Repair', 'For Repair'),
        ('No Maintenance Record', 'No Maintenance Record'),
        ('Disposed', 'Disposed'),
    ]

    # Link to the Virtual Model using the column name 'asset_id' found in your Supabase schema
    asset = models.ForeignKey(
        Asset, 
        db_column='asset_id', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='vehicle_details'
    )
    
    vehicle_id = models.CharField(max_length=50, null=True, blank=True)
    kind = models.CharField(max_length=50, null=True, blank=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.CharField(max_length=4, null=True, blank=True)
    plate_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    conduction_number = models.CharField(max_length=20, null=True, blank=True)
    engine_number = models.CharField(max_length=50, null=True, blank=True)
    chassis_number = models.CharField(max_length=50, null=True, blank=True)
    
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES, 
        default='No Maintenance Record'
    )
    odometer_reading = models.IntegerField(default=0)
    
    registration_renewal_date = models.DateField(null=True, blank=True)
    insurance_renewal_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.plate_number or self.conduction_number})"

class PARRecord(models.Model):
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='par_records')
    par_number = models.CharField(max_length=50, unique=True)
    
    fund_cluster = models.CharField(max_length=100, blank=True, null=True)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    
    issued_to = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True, null=True)
    date_issued = models.DateField(default=timezone.now)
    
    expiry_date = models.DateField(blank=True, null=True)
    
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.par_number} - {self.issued_to}"

    class Meta:
        verbose_name = "PAR Record"
        verbose_name_plural = "PAR Records"
        ordering = ['-date_issued']

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=10)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_action_type_display(self):
        return self.action_type.capitalize()