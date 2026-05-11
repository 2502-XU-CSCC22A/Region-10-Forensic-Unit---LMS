from django import forms
from .models import Communication, CommunicationPARRecord, CommunicationICSRecord


class CommunicationPARForm(forms.ModelForm):

    class Meta:
        model = CommunicationPARRecord

        fields = [
            "communication",
            "par_number",
            "reference_no",
            "issued_to",
            "date_issued",
            "expiry_date",
            "remarks",
        ]

        widgets = {
            "communication": forms.Select(attrs={"class": "form-select"}),
            "par_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter PAR Number"}
            ),
            "reference_no": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Reference Number"}
            ),
            "issued_to": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Personnel Name"}
            ),
            "date_issued": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "expiry_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "remarks": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                    "placeholder": "Enter remarks",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        current_communication = None

        if self.instance and self.instance.pk:
            current_communication = self.instance.communication_id

        used_communication_ids = CommunicationPARRecord.objects.exclude(
            pk=self.instance.pk if self.instance and self.instance.pk else None
        ).values_list("communication_id", flat=True)

        queryset = Communication.objects.exclude(
            asset_ptr_id__in=used_communication_ids
        ).exclude(
            status_id__in=[4, 5, 7]
        )

        if current_communication:
            queryset = queryset | Communication.objects.filter(
                asset_ptr_id=current_communication
            )

        self.fields["communication"].queryset = queryset.distinct()

        self.fields["communication"].label = "COMMUNICATION ASSET"
        self.fields["par_number"].label = "PAR NO."
        self.fields["reference_no"].label = "REFERENCE NO."
        self.fields["issued_to"].label = "ISSUED TO"
        self.fields["date_issued"].label = "DATE ISSUED"
        self.fields["expiry_date"].label = "EXPIRY DATE"
        self.fields["remarks"].label = "REMARKS"

    def clean_par_number(self):

        par_number = self.cleaned_data.get("par_number")

        if not par_number:
            return par_number

        qs = CommunicationPARRecord.objects.filter(par_number__iexact=par_number)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This PAR number already exists.")
        return par_number

    def clean_reference_no(self):

        reference_no = self.cleaned_data.get("reference_no")

        if not reference_no:
            return reference_no

        qs = CommunicationPARRecord.objects.filter(reference_no__iexact=reference_no)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This PAR reference number already exists.")
        return reference_no


class CommunicationICSForm(forms.ModelForm):

    class Meta:
        model = CommunicationICSRecord

        fields = [
            "communication",
            "ics_number",
            "reference_no",
            "issued_to",
            "date_issued",
            "expiry_date",
            "remarks",
        ]

        widgets = {
            "communication": forms.Select(attrs={"class": "form-select"}),
            "ics_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter ICS Number"}
            ),
            "reference_no": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Reference Number"}
            ),
            "issued_to": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter Personnel Name"}
            ),
            "date_issued": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "expiry_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "remarks": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                    "placeholder": "Enter remarks",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        current_communication = None

        if self.instance and self.instance.pk:
            current_communication = self.instance.communication_id

        used_communication_ids = CommunicationICSRecord.objects.exclude(
            pk=self.instance.pk if self.instance and self.instance.pk else None
        ).values_list("communication_id", flat=True)

        queryset = Communication.objects.exclude(
            asset_ptr_id__in=used_communication_ids
        ).exclude(
            status_id__in=[4, 5, 7]
        )

        if current_communication:
            queryset = queryset | Communication.objects.filter(
                asset_ptr_id=current_communication
            )

        self.fields["communication"].queryset = queryset.distinct()

        self.fields["communication"].label = "COMMUNICATION ASSET"
        self.fields["ics_number"].label = "ICS NO."
        self.fields["reference_no"].label = "REFERENCE NO."
        self.fields["issued_to"].label = "ISSUED TO"
        self.fields["date_issued"].label = "DATE ISSUED"
        self.fields["expiry_date"].label = "EXPIRY DATE"
        self.fields["remarks"].label = "REMARKS"

    def clean_ics_number(self):

        ics_number = self.cleaned_data.get("ics_number")

        if not ics_number:
            return ics_number

        qs = CommunicationICSRecord.objects.filter(ics_number__iexact=ics_number)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This ICS number already exists.")
        return ics_number

    def clean_reference_no(self):

        reference_no = self.cleaned_data.get("reference_no")

        if not reference_no:
            return reference_no

        qs = CommunicationICSRecord.objects.filter(reference_no__iexact=reference_no)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This ICS reference number already exists.")
        return reference_no
