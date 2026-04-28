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
        # Ensure 'vehicle' is included to provide the foreign key dropdown selection
        fields = ['vehicle', 'par_number', 'issued_to', 'date_issued', 'remarks']
        widgets = {
            'date_issued': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Applying Bootstrap styles based on input type
            if field_name == 'vehicle':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Labels specifically formatted to match the PAR management screenshot
        self.fields['vehicle'].label = "SELECT VEHICLE"
        self.fields['par_number'].label = "PAR NUMBER"
        self.fields['issued_to'].label = "ISSUED TO (PERSONNEL)"
        self.fields['date_issued'].label = "DATE ISSUED"
        self.fields['remarks'].label = "REMARKS / NOTES"