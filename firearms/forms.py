from django import forms


class FirearmsPARForm(forms.Form):

    par_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "PAR-2026-001"}
        ),
        label="PAR NO.",
    )

    fund_cluster = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Fund Cluster"}
        ),
        label="FUND CLUSTER",
    )

    firearm = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="FIREARM ASSET",
    )

    reference_no = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Reference Number"}
        ),
        label="REFERENCE NO.",
    )

    issued_to = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Personnel Name"}
        ),
        label="ISSUED TO",
    )

    date_issued = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="DATE ISSUED",
    )

    expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="EXPIRY DATE",
    )

    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "class": "form-control",
                "placeholder": "Enter remarks...",
            }
        ),
        label="REMARKS",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["date_issued"].initial = __import__("datetime").date.today()

        try:
            from firearms.models import Firearm, FirearmPARRecord

            used_firearm_ids = FirearmPARRecord.objects.exclude(
                firearm_id__isnull=True
            ).values_list("firearm_id", flat=True)

            firearms = (
                Firearm.objects.exclude(pk__in=used_firearm_ids)
                .exclude(status_id__in=[4, 5, 7])
                .values_list("id", "serial_no", "model")
            )
            
            self.fields["firearm"].widget.choices = [("", "---------")] + [
                (f[0], f"{f[2]} / SN: {f[1]}") for f in firearms
            ]

        except Exception:
            self.fields["firearm"].widget.choices = [
                ("", "---------"),
            ]
