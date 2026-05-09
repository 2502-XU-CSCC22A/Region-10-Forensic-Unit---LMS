from django import forms
from .models import Vehicle, PARRecord


class VehicleForm(forms.ModelForm):
    par_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter PAR number'
        })
    )

    issued_to = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter accountable person'
        })
    )

    date_acquired = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Enter remarks'
        })
    )

    class Meta:
        model = Vehicle

        fields = [
            'vehicle_id',
            'plate_number',
            'primary_driver',
            'alternative_driver',
            'classification',
            'make_model',
            'year',
            'conduction_number',
            'status',
            'engine_number',
            'chassis_number',
            'registration_renewal_date',
            'insurance_renewal_date',
        ]

        widgets = {
            'vehicle_id': forms.TextInput(attrs={'class': 'form-control'}),
            'plate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_driver': forms.TextInput(attrs={'class': 'form-control'}),
            'alternative_driver': forms.TextInput(attrs={'class': 'form-control'}),
            'classification': forms.Select(attrs={'class': 'form-select'}),
            'make_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Toyota Hilux'
            }),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'conduction_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control'}),
            'chassis_number': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_renewal_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'insurance_renewal_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mobility can flag BER, but only Disposal/BER module should set Disposed.
        self.fields['status'].choices = [
            ('Serviceable', 'Serviceable'),
            ('Unserviceable', 'Unserviceable'),
            ('BER', 'BER'),
        ]

        labels = {
            'vehicle_id': 'VEHICLE ID',
            'plate_number': 'PLATE NUMBER',
            'primary_driver': 'PRIMARY DRIVER',
            'alternative_driver': 'ALTERNATIVE DRIVER',
            'classification': 'VEHICLE CLASSIFICATION',
            'make_model': 'MAKE / MODEL',
            'year': 'YEAR',
            'conduction_number': 'CONDUCTION NUMBER',
            'status': 'STATUS',
            'engine_number': 'ENGINE NUMBER',
            'chassis_number': 'CHASSIS NUMBER',
            'registration_renewal_date': 'REGISTRATION RENEWAL DATE',
            'insurance_renewal_date': 'INSURANCE RENEWAL DATE',
            'par_number': 'PAR NUMBER',
            'issued_to': 'ISSUED TO',
            'date_acquired': 'DATE ACQUIRED',
            'expiry_date': 'EXPIRY DATE',
            'remarks': 'REMARKS',
        }

        for field_name, field in self.fields.items():
            field.label = labels.get(
                field_name,
                field_name.replace('_', ' ').upper()
            )

            if field_name in ['classification', 'status']:
                field.widget.attrs.update({'class': 'form-select'})
            elif 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})


class PARForm(forms.ModelForm):
    class Meta:
        model = PARRecord

        fields = [
            'vehicle',
            'par_number',
            'issued_to',
            'date_acquired',
            'expiry_date',
            'remarks',
        ]

        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'par_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issued_to': forms.TextInput(attrs={'class': 'form-control'}),
            'date_acquired': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'expiry_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'remarks': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['vehicle'].label = "VEHICLE"
        self.fields['par_number'].label = "PAR NUMBER"
        self.fields['issued_to'].label = "ISSUED TO"
        self.fields['date_acquired'].label = "DATE ACQUIRED"
        self.fields['expiry_date'].label = "EXPIRY DATE"
        self.fields['remarks'].label = "REMARKS"