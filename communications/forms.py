from django import forms
from .models import CommunicationPARRecord


class CommunicationPARForm(forms.ModelForm):
    class Meta:
        model = CommunicationPARRecord
        fields = [
            "communication",
            "par_number",
            "fund_cluster",
            "reference_no",
            "issued_to",
            "date_issued",
            "expiry_date",
            "remarks",
        ]

        widgets = {
            "date_issued": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "expiry_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "remarks": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name == "communication":
                field.widget.attrs.update({"class": "form-select"})
            elif field_name not in ["date_issued", "expiry_date", "remarks"]:
                field.widget.attrs.update({"class": "form-control"})

        self.fields["communication"].label = "COMMUNICATION ASSET"
        self.fields["par_number"].label = "PAR NO."
        self.fields["fund_cluster"].label = "FUND CLUSTER"
        self.fields["reference_no"].label = "REFERENCE NO."
        self.fields["issued_to"].label = "ISSUED TO"
        self.fields["date_issued"].label = "DATE ISSUED"
        self.fields["expiry_date"].label = "EXPIRY DATE"
        self.fields["remarks"].label = "REMARKS"