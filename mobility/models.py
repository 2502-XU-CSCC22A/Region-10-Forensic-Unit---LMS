from django.db import models
from config.models import Asset
from django.contrib.auth.models import User
from django.utils import timezone
from config.models import Asset

class ConfigAsset(models.Model):
    class Meta:
        managed = False  # Django will not try to modify this table
        db_table = 'config_asset'
    
    property_no = models.CharField(max_length=100)

    def __str__(self):
        return self.property_no

class Vehicle(models.Model):
    # Link to the main Asset registry
    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='vehicle_details')
    
    # Basic Information
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.CharField(max_length=4, null=True, blank=True)
    
    # Identification
    plate_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    conduction_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    engine_number = models.CharField(max_length=100, null=True, blank=True)
    chassis_number = models.CharField(max_length=100, null=True, blank=True)
    
    # Status and Logistics
    kind = models.CharField(max_length=50, default="Vehicle")
    status = models.CharField(max_length=50, default="Good Condition")
    latest_odo = models.PositiveIntegerField(default=0)
    
    # Compliance and Maintenance
    registration_renewal_date = models.DateField(null=True, blank=True)
    insurance_renewal_date = models.DateField(null=True, blank=True)
    
    # Audit Trail
    created_at = models.DateTimeField(default=timezone.now) 
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.plate_number or self.conduction_number})"

class PARRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='par_records')
    issued_to = models.CharField(max_length=255)
    date_issued = models.DateField()
    is_active = models.BooleanField(default=True)
    date_returned = models.DateField(null=True, blank=True)
    
    # Technical Fields for the Region-10 Forensic Unit Registry
    par_number = models.CharField(max_length=100, null=True, blank=True)
    fund_cluster = models.CharField(max_length=100, null=True, blank=True)
    reference_no = models.CharField(max_length=100, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"PAR: {self.par_number or 'Unnumbered'} - {self.issued_to}"

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    action = models.CharField(max_length=50, default='UNKNOWN')
    details = models.TextField(default='No details provided')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action}"