from django import forms

from config.models import Asset
from .models import InvestigativePARRecord, ICSRecord


class InvestigativePARForm(forms.ModelForm):
    class Meta:
        model = InvestigativePARRecord

        fields = [
            "asset",
            "par_number",
            "reference_no",
            "issued_to",
            "date_issued",
            "expiry_date",
            "remarks",
        ]

        widgets = {
            "asset": forms.Select(attrs={"class": "form-select"}),
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

        current_asset = None

        if self.instance and self.instance.pk:
            current_asset = self.instance.asset_id

        used_asset_ids = InvestigativePARRecord.objects.exclude(
            pk=self.instance.pk if self.instance and self.instance.pk else None
        ).values_list("asset_id", flat=True)

        queryset = (
            Asset.objects.filter(investigative_details__isnull=False)
            .exclude(id__in=used_asset_ids)
            .exclude(status_id__in=[4, 5, 7])
        )

        if current_asset:
            queryset = queryset | Asset.objects.filter(id=current_asset)

        self.fields["asset"].queryset = queryset.distinct()

        self.fields["asset"].label = "INVESTIGATIVE ASSET"
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

        qs = InvestigativePARRecord.objects.filter(par_number__iexact=par_number)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This PAR number already exists.")

        return par_number

    def clean_reference_no(self):
        reference_no = self.cleaned_data.get("reference_no")

        if not reference_no:
            return reference_no

        qs = InvestigativePARRecord.objects.filter(reference_no__iexact=reference_no)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This PAR reference number already exists.")

        return reference_no


class InvestigativeICSForm(forms.ModelForm):
    class Meta:
        model = ICSRecord

        fields = [
            "asset",
            "ics_number",
            "reference_no",
            "issued_to",
            "date_issued",
            "expiry_date",
            "remarks",
        ]

        widgets = {
            "asset": forms.Select(attrs={"class": "form-select"}),
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

        current_asset = None

        if self.instance and self.instance.pk:
            current_asset = self.instance.asset_id

        used_asset_ids = ICSRecord.objects.exclude(
            pk=self.instance.pk if self.instance and self.instance.pk else None
        ).values_list("asset_id", flat=True)

        queryset = (
            Asset.objects.filter(investigative_details__isnull=False)
            .exclude(id__in=used_asset_ids)
            .exclude(status_id__in=[4, 5, 7])
        )

        if current_asset:
            queryset = queryset | Asset.objects.filter(id=current_asset)

        self.fields["asset"].queryset = queryset.distinct()

        self.fields["asset"].label = "INVESTIGATIVE ASSET"
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

        qs = ICSRecord.objects.filter(ics_number__iexact=ics_number)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This ICS number already exists.")

        return ics_number

    def clean_reference_no(self):
        reference_no = self.cleaned_data.get("reference_no")

        if not reference_no:
            return reference_no

        qs = ICSRecord.objects.filter(reference_no__iexact=reference_no)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This ICS reference number already exists.")

        return reference_no
