from django import forms
from .models import Vehicle, PARRecord

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        # These names MUST match the new names in your models.py exactly
        fields = [
            'vehicle_id', 
            'kind', 
            'make', 
            'model', 
            'year', 
            'plate_number', 
            'conduction_number', 
            'engine_number', 
            'chassis_number', 
            'status', 
            'latest_odo', 
            'registration_renewal_date', 
            'insurance_renewal_date'
        ]
        widgets = {
            'registration_renewal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'insurance_renewal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'kind': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Special Purpose Vehicle'}),
            'make': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'latest_odo': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(VehicleForm, self).__init__(*args, **kwargs)
        # This prevents the "This field is required" errors from blocking the save
        self.fields['kind'].required = False
        self.fields['make'].required = False
        self.fields['latest_odo'].required = False
        # You can add more fields here if you want them to be optional too
        self.fields['model'].required = False
        self.fields['year'].required = False

class PARForm(forms.ModelForm):
    class Meta:
        model = PARRecord
        fields = ['vehicle', 'par_number', 'issued_to', 'date_issued', 'remarks']
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
        }