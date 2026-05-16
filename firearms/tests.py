from django.test import TestCase
from django.utils import timezone
from config.models import Category

from .forms import FirearmsPARForm
from .models import Firearm, FirearmPARRecord


def create_category():
    category = Category()

    for field in Category._meta.fields:
        if field.get_internal_type() == "CharField":
            setattr(category, field.name, "Firearms")
            break

    category.save()
    return category


class FirearmsPARFormTest(TestCase):

    def setUp(self):
        self.category = create_category()

        self.firearm = Firearm.objects.create(
            type="GLOCK 19 / PISTOL / 9MM",
            caliber="9MM",
            faid_serial="SFA20324",
            assigned_to="PRECIOUS PAGUTE",
            unit="RFU 10",
            subunit="CRIME LAB",
            station="MALAYBALAY CITY",
            issuing_unit="PNP FG",
            date_acquired=timezone.now().date(),
            property_no="PROP-FIREARM-001",
            serial_no="SFA20324",
            model="GLOCK 19",
            category=self.category,
        )

        self.par = FirearmPARRecord.objects.create(
            firearm=self.firearm,
            par_number="PAR-2026-001",
            reference_no="REF-001",
            issued_to="Officer Juan",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="Test PAR",
        )

    def test_duplicate_par_number_is_invalid(self):
        form = FirearmsPARForm(
            data={
                "firearm": self.firearm.asset_ptr_id,
                "par_number": "PAR-2026-001",
                "fund_cluster": "Test Fund",
                "reference_no": "REF-NEW",
                "issued_to": "Officer Pedro",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate PAR number",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("par_number", form.errors)

    def test_duplicate_reference_no_is_invalid(self):
        form = FirearmsPARForm(
            data={
                "firearm": self.firearm.asset_ptr_id,
                "par_number": "PAR-NEW",
                "fund_cluster": "Test Fund",
                "reference_no": "REF-001",
                "issued_to": "Officer Pedro",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate reference number",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("reference_no", form.errors)

    def test_used_firearm_not_shown_in_par_dropdown(self):
        form = FirearmsPARForm()

        used_firearm_ids = [
            choice[0]
            for choice in form.fields["firearm"].widget.choices
        ]

        self.assertNotIn(self.firearm.asset_ptr_id, used_firearm_ids)

    def test_new_par_form_is_valid_for_unused_firearm(self):
        unused_firearm = Firearm.objects.create(
            type="AK47 / PERIOD / 14 MM",
            caliber="14 MM",
            faid_serial="SFA20219",
            assigned_to="GIRL EYE",
            unit="RFU 10",
            subunit="CRIME LAB",
            station="BUTUAN CITY",
            issuing_unit="PNP FG",
            date_acquired=timezone.now().date(),
            property_no="PROP-FIREARM-002",
            serial_no="SFA20219",
            model="AK47",
            category=self.category,
        )

        form = FirearmsPARForm(
            data={
                "firearm": unused_firearm.asset_ptr_id,
                "par_number": "PAR-2026-002",
                "fund_cluster": "Test Fund",
                "reference_no": "REF-002",
                "issued_to": "Officer Maria",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Valid PAR",
            }
        )

        self.assertTrue(form.is_valid())