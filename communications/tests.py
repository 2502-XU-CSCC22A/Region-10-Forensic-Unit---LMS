from django.test import TestCase
from django.utils import timezone

from config.models import Category, AssetStatus
from .forms import CommunicationPARForm, CommunicationICSForm
from .models import (
    Communication,
    CommunicationPARRecord,
    CommunicationICSRecord,
)


def create_category():
    return Category.objects.get_or_create(category_name="communications")[0]


def create_status(status_id=1, status_name="Available"):
    return AssetStatus.objects.get_or_create(
        status_id=status_id,
        defaults={"status_name": status_name},
    )[0]


def create_communication(
    property_no="PROP-001",
    serial_no="SERIAL-001",
    imei_serial="IMEI-001",
    status_id=1,
    status_name="Available",
):

    category = create_category()

    status = create_status(status_id, status_name)

    return Communication.objects.create(
        type="Radio",
        imei_serial=imei_serial,
        radio_id="RAD-001",
        remarks="VALIDATED",
        is_deleted=False,
        date_acquired=timezone.now().date(),
        property_no=property_no,
        serial_no=serial_no,
        model="Motorola",
        quantity="1",
        status=status,
        category=category,
    )


class CommunicationModelTest(TestCase):

    def test_communication_string_output(self):

        comm = create_communication()

        self.assertEqual(str(comm), "Radio - IMEI-001")


class CommunicationPARFormTest(TestCase):

    def setUp(self):

        self.comm = create_communication()

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

    def test_ber_disposed_and_unserviceable_not_shown_in_par_dropdown(self):

        ber = create_communication(
            "PROP-BER",
            "SER-BER",
            "IMEI-BER",
            4,
            "BER",
        )

        disposed = create_communication(
            "PROP-DISP",
            "SER-DISP",
            "IMEI-DISP",
            5,
            "Disposed",
        )

        unserviceable = create_communication(
            "PROP-UNSERV",
            "SER-UNSERV",
            "IMEI-UNSERV",
            7,
            "Unserviceable",
        )

        form = CommunicationPARForm()

        queryset = form.fields["communication"].queryset

        self.assertNotIn(ber, queryset)

        self.assertNotIn(disposed, queryset)

        self.assertNotIn(unserviceable, queryset)

    def test_available_communication_shown_in_par_dropdown(self):

        available = create_communication(
            "PROP-002",
            "SERIAL-002",
            "IMEI-002",
            1,
            "Available",
        )

        form = CommunicationPARForm()

        self.assertIn(available, form.fields["communication"].queryset)


class CommunicationICSFormTest(TestCase):

    def setUp(self):

        self.comm = create_communication(
            property_no="PROP-ICS-001",
            serial_no="SERIAL-ICS-001",
            imei_serial="IMEI-ICS-001",
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

    def test_ber_disposed_and_unserviceable_not_shown_in_ics_dropdown(self):

        ber = create_communication(
            "PROP-BER2",
            "SER-BER2",
            "IMEI-BER2",
            4,
            "BER",
        )

        disposed = create_communication(
            "PROP-DISP2",
            "SER-DISP2",
            "IMEI-DISP2",
            5,
            "Disposed",
        )

        unserviceable = create_communication(
            "PROP-UNSERV2",
            "SER-UNSERV2",
            "IMEI-UNSERV2",
            7,
            "Unserviceable",
        )

        form = CommunicationICSForm()

        queryset = form.fields["communication"].queryset

        self.assertNotIn(ber, queryset)

        self.assertNotIn(disposed, queryset)

        self.assertNotIn(unserviceable, queryset)

    def test_available_communication_shown_in_ics_dropdown(self):

        available = create_communication(
            "PROP-ICS-002",
            "SERIAL-ICS-002",
            "IMEI-ICS-002",
            1,
            "Available",
        )

        form = CommunicationICSForm()

        self.assertIn(available, form.fields["communication"].queryset)
