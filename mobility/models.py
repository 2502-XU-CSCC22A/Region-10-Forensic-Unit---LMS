from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

class Vehicle(models.Model):
    # Unique identifier for the PNP Forensic Unit vehicle
    vehicle_id = models.CharField(max_length=100, unique=True)  
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    
    status_choices = [
        ('Available', 'Available'),
        ('In Use', 'In Use'),
        ('Maintenance', 'Maintenance'),
    ]
    # Increased max_length slightly for safety
    status = models.CharField(max_length=25, choices=status_choices, default='Available')

    engine_number = models.CharField(max_length=100, blank=True)
    chassis_number = models.CharField(max_length=100, blank=True)
    
    registration_renewal_date = models.DateField(null=True, blank=True)
    insurance_renewal_date = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ['vehicle_id'] # Keeps your list organized by ID

    def clean(self):
        # Validation for future dates
        if self.registration_renewal_date and self.registration_renewal_date < date.today():
            raise ValidationError({'registration_renewal_date': "Registration renewal date must be in the future."})
        if self.insurance_renewal_date and self.insurance_renewal_date < date.today():
            raise ValidationError({'insurance_renewal_date': "Insurance renewal date must be in the future."})
        super().clean()

    def __str__(self):
        return f"{self.model} ({self.vehicle_id})"