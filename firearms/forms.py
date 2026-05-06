from django import forms


# ============================================================
# FIREARMS PAR FORM (standalone - no model dependency yet)
# ============================================================

class FirearmsPARForm(forms.Form):
    """
    Standalone PAR form for the Firearms app.
    Works without CommunicationPARRecord model from the communications branch.
    When your teammates merge their branch, switch to ModelForm if needed.
    """
    
    par_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PAR-2026-001'
        }),
        label='PAR NO.'
    )
    
    fund_cluster = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Fund Cluster'
        }),
        label='FUND CLUSTER'
    )
    
    # CHANGED: renamed from 'vehicle' to 'firearm', label updated to FIREARM ASSET
    firearm = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='FIREARM ASSET'
    )
    
    reference_no = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reference Number'
        }),
        label='REFERENCE NO.'
    )
    
    issued_to = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Personnel Name'
        }),
        label='ISSUED TO'
    )
    
    date_issued = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='DATE ISSUED'
    )
    
    expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label='EXPIRY DATE'
    )
    
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter remarks...'
        }),
        label='REMARKS'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial date to today
        self.fields['date_issued'].initial = __import__('datetime').date.today()
        
        # CHANGED: Populate firearm choices from Firearm model instead of vehicle
        try:
            from firearms.models import Firearm
            firearms = Firearm.objects.values_list('id', 'serial_no', 'model')
            self.fields['firearm'].widget.choices = (
                [('', '---------')] +
                [(f[0], f'{f[2]} / SN: {f[1]}') for f in firearms]
            )
        except Exception:
            self.fields['firearm'].widget.choices = [
                ('', '---------'),
                ('1', 'AK47 / SN: AGG8'),
            ]