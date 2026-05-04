from django import forms
from .models import Vehicle, PARRecord

class VehicleForm(forms.ModelForm):
    # This maps the manual odometer input to the model's odometer_reading
    latest_odo = forms.IntegerField(label="LATEST ODOMETER", required=False)

    class Meta:
        model = Vehicle
        fields = [
            'asset', 'vehicle_id', 'kind', 'make', 'model', 
            'year', 'plate_number', 'conduction_number', 'status',
            'engine_number', 'chassis_number', 
            'latest_odo', 
            'registration_renewal_date', 'insurance_renewal_date'
        ]
        widgets = {
            # Explicitly using Select widget for the Status dropdown logic
            'status': forms.Select(attrs={'class': 'form-control'}),
            'registration_renewal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'insurance_renewal_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent Bootstrap styling and uppercase labels for aesthetics
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            field.label = field.label.upper() if field.label else field_name.replace('_', ' ').upper()
            
        if self.instance and self.instance.pk:
            self.fields['latest_odo'].initial = self.instance.odometer_reading

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Transfer the latest_odo value to the odometer_reading field before saving
        instance.odometer_reading = self.cleaned_data.get('latest_odo') or 0
        if commit:
            instance.save()
        return instance

class PARForm(forms.ModelForm):
    class Meta:
        model = PARRecord
        # Added fund_cluster, reference_no, and expiry_date to match the PNP receipt requirements
        fields = [
            'vehicle', 
            'par_number', 
            'fund_cluster', 
            'reference_no', 
            'issued_to', 
            'date_issued', 
            'expiry_date', 
            'remarks'
        ]
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Bootstrap classes dynamically
        for field_name, field in self.fields.items():
            if field_name == 'vehicle':
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name not in ['date_issued', 'expiry_date', 'remarks']:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Labels updated to match your management dashboard UI
        self.fields['vehicle'].label = "VEHICLE ASSET"
        self.fields['par_number'].label = "PAR NO."
        self.fields['fund_cluster'].label = "FUND CLUSTER"
        self.fields['reference_no'].label = "REFERENCE NO."
        self.fields['issued_to'].label = "ISSUED TO (NAME)"
        self.fields['date_issued'].label = "DATE ISSUED"
        self.fields['expiry_date'].label = "EXPIRY DATE"
        self.fields['remarks'].label = "REMARKS / NOTES"