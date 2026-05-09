from django.test import TestCase
from django.utils import timezone
from config.models import Category

from .forms import CommunicationPARForm, CommunicationICSForm
from .models import Communication, CommunicationPARRecord, CommunicationICSRecord


def create_category():
    category = Category()

    for field in Category._meta.fields:
        if field.get_internal_type() == "CharField":
            setattr(category, field.name, "Communications")
            break

    category.save()
    return category


class CommunicationPARFormTest(TestCase):

    def setUp(self):
        self.category = create_category()

        self.comm = Communication.objects.create(
            type="Radio",
            imei_serial="IMEI-001",
            date_acquired=timezone.now().date(),
            property_no="PROP-001",
            serial_no="SERIAL-001",
            model="Motorola",
            category=self.category,
        )

        self.par = CommunicationPARRecord.objects.create(
            communication=self.comm,
            par_number="PAR-001",
            reference_no="REF-001",
            issued_to="Officer Juan",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="Test PAR",
        )

    def test_duplicate_par_number_is_invalid(self):
        form = CommunicationPARForm(
            data={
                "communication": self.comm.asset_ptr_id,
                "par_number": "PAR-001",
                "reference_no": "REF-NEW",
                "issued_to": "Officer Pedro",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate PAR number",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("par_number", form.errors)

    def test_duplicate_par_reference_no_is_invalid(self):
        form = CommunicationPARForm(
            data={
                "communication": self.comm.asset_ptr_id,
                "par_number": "PAR-NEW",
                "reference_no": "REF-001",
                "issued_to": "Officer Pedro",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate reference",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("reference_no", form.errors)

    def test_used_communication_not_shown_in_par_dropdown(self):
        form = CommunicationPARForm()

        self.assertNotIn(self.comm, form.fields["communication"].queryset)


class CommunicationICSFormTest(TestCase):

    def setUp(self):
        self.category = create_category()

        self.comm = Communication.objects.create(
            type="Handheld Radio",
            imei_serial="IMEI-002",
            date_acquired=timezone.now().date(),
            property_no="PROP-002",
            serial_no="SERIAL-002",
            model="Kenwood",
            category=self.category,
        )

        self.ics = CommunicationICSRecord.objects.create(
            communication=self.comm,
            ics_number="ICS-001",
            reference_no="ICS-REF-001",
            issued_to="Officer Maria",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="Test ICS",
        )

    def test_duplicate_ics_number_is_invalid(self):
        form = CommunicationICSForm(
            data={
                "communication": self.comm.asset_ptr_id,
                "ics_number": "ICS-001",
                "reference_no": "ICS-REF-NEW",
                "issued_to": "Officer Ana",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate ICS number",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("ics_number", form.errors)

    def test_duplicate_ics_reference_no_is_invalid(self):
        form = CommunicationICSForm(
            data={
                "communication": self.comm.asset_ptr_id,
                "ics_number": "ICS-NEW",
                "reference_no": "ICS-REF-001",
                "issued_to": "Officer Ana",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate reference",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("reference_no", form.errors)

    def test_used_communication_not_shown_in_ics_dropdown(self):
        form = CommunicationICSForm()

        self.assertNotIn(self.comm, form.fields["communication"].queryset)