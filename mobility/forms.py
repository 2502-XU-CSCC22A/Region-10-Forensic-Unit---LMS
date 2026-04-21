# mobility/forms.py
from django import forms
from .models import Vehicle

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_id', 'model', 'year', 'status', 
            'engine_number', 'chassis_number', 
            'registration_renewal_date', 'insurance_renewal_date'
        ]
        # Adding widgets makes the form much easier to use
        widgets = {
            'registration_renewal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'insurance_renewal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vehicle_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. FU-2026-001'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control'}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control'}),
        }