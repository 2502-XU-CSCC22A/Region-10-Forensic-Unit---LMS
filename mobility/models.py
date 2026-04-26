from django.db import models
from django.utils import timezone

class Vehicle(models.Model):
    # Identity
    vehicle_id = models.CharField(max_length=50, unique=True, default="TEMP-ID")
    kind = models.CharField(max_length=100, default="Special Purpose Vehicle")
    make = models.CharField(max_length=100) 
    model = models.CharField(max_length=100) 
    year = models.IntegerField(default=2024)
    
    # Registration & Technical
    plate_number = models.CharField(max_length=50, blank=True, null=True)
    conduction_number = models.CharField(max_length=50, blank=True, null=True)
    engine_number = models.CharField(max_length=100, unique=True)
    chassis_number = models.CharField(max_length=100, unique=True)
    
    # Tracking & Status
    STATUS_CHOICES = [
        ('Good', 'Good'), 
        ('No Record', 'No Record'),
        ('For PMS', 'For PMS'), 
        ('For Registration', 'For Registration'),
        ('For Insurance', 'For Insurance'),
        ('Repair Required', 'Repair Required'),
        ('Upcoming PMS', 'Upcoming PMS'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Good')
    latest_odo = models.IntegerField(default=0)
    
    # Renewal Dates
    registration_renewal_date = models.DateField(null=True, blank=True)
    insurance_renewal_date = models.DateField(null=True, blank=True)
    
    # Metadata for History
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.make} {self.model} ({self.plate_number or self.conduction_number})"

class PARRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='pars')
    par_number = models.CharField(max_length=100, unique=True)
    issued_to = models.CharField(max_length=255)
    date_issued = models.DateField(default=timezone.now)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.par_number} - {self.issued_to}"

class ActivityLog(models.Model):
    ACTION_TYPES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type}: {self.description} at {self.timestamp}"