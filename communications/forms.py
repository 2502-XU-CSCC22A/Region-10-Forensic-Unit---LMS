from django import forms
from .models import CommunicationPARRecord


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

            "communication": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "par_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter PAR Number"
                }
            ),

            "reference_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Reference Number"
                }
            ),

            "issued_to": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Personnel Name"
                }
            ),

            "date_issued": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "expiry_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "form-control",
                    "placeholder": "Enter remarks"
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["communication"].label = "COMMUNICATION ASSET"

        self.fields["par_number"].label = "PAR NO."

        self.fields["reference_no"].label = "REFERENCE NO."

        self.fields["issued_to"].label = "ISSUED TO"

        self.fields["date_issued"].label = "DATE ISSUED"

        self.fields["expiry_date"].label = "EXPIRY DATE"

        self.fields["remarks"].label = "REMARKS"

    def clean_par_number(self):

        par_number = self.cleaned_data.get(
            "par_number"
        )

        if not par_number:
            return par_number

        qs = CommunicationPARRecord.objects.filter(
            par_number__iexact=par_number
        )

        if self.instance.pk:
            qs = qs.exclude(
                pk=self.instance.pk
            )

        if qs.exists():

            raise forms.ValidationError(
                "This PAR number already exists."
            )

        return par_number