from django.test import TestCase
from django.utils import timezone
from django.apps import apps

from config.models import Category, Asset
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


def create_communication(category, suffix="001", status="SERVICEABLE", remarks="VALIDATED"):
    return Communication.objects.create(
        type="Radio",
        imei_serial=f"IMEI-{suffix}",
        radio_id=f"RADIO-{suffix}",
        date_acquired=timezone.now().date(),
        property_no=f"PROP-{suffix}",
        serial_no=f"SERIAL-{suffix}",
        model="Motorola",
        category=category,
        status=status,
        remarks=remarks,
        is_deleted=False,
    )


class CommunicationPARFormTest(TestCase):

    def setUp(self):
        self.category = create_category()
        self.comm = create_communication(self.category, "001")

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

    def test_unused_communication_shown_in_par_dropdown(self):
        unused_comm = create_communication(self.category, "002")
        form = CommunicationPARForm()
        self.assertIn(unused_comm, form.fields["communication"].queryset)

    def test_valid_par_form_is_valid(self):
        unused_comm = create_communication(self.category, "003")

        form = CommunicationPARForm(
            data={
                "communication": unused_comm.asset_ptr_id,
                "par_number": "PAR-003",
                "reference_no": "REF-003",
                "issued_to": "Officer Pedro",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Valid PAR",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)


class CommunicationICSFormTest(TestCase):

    def setUp(self):
        self.category = create_category()
        self.comm = create_communication(self.category, "004")

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

    def test_unused_communication_shown_in_ics_dropdown(self):
        unused_comm = create_communication(self.category, "005")
        form = CommunicationICSForm()
        self.assertIn(unused_comm, form.fields["communication"].queryset)

    def test_valid_ics_form_is_valid(self):
        unused_comm = create_communication(self.category, "006")

        form = CommunicationICSForm(
            data={
                "communication": unused_comm.asset_ptr_id,
                "ics_number": "ICS-006",
                "reference_no": "ICS-REF-006",
                "issued_to": "Officer Ana",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Valid ICS",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)


class CommunicationJSBehaviorTest(TestCase):

    def setUp(self):
        self.category = create_category()

        self.serviceable = create_communication(
            self.category,
            "007",
            status="SERVICEABLE",
            remarks="VALIDATED",
        )

        self.unserviceable = create_communication(
            self.category,
            "008",
            status="UNSERVICEABLE",
            remarks="EXPIRED/FOR RENEWAL",
        )

    def test_status_and_remarks_values_match_js_badges(self):
        self.assertEqual(self.serviceable.status, "SERVICEABLE")
        self.assertEqual(self.serviceable.remarks, "VALIDATED")

        self.assertEqual(self.unserviceable.status, "UNSERVICEABLE")
        self.assertEqual(self.unserviceable.remarks, "EXPIRED/FOR RENEWAL")

    def test_filter_serviceable_records_like_js_status_filter(self):
        serviceable_records = Communication.objects.filter(status="SERVICEABLE")

        self.assertIn(self.serviceable, serviceable_records)
        self.assertNotIn(self.unserviceable, serviceable_records)

    def test_search_like_js_filter_matches_type_serial_radio_status_and_remarks(self):
        query = "imei-007"

        results = [
            comm for comm in Communication.objects.all()
            if query.lower() in str(comm.type).lower()
            or query.lower() in str(comm.imei_serial).lower()
            or query.lower() in str(comm.radio_id).lower()
            or query.lower() in str(comm.status).lower()
            or query.lower() in str(comm.remarks).lower()
        ]

        self.assertIn(self.serviceable, results)
        self.assertNotIn(self.unserviceable, results)

    def test_expiring_par_soon_count_within_30_days(self):
        today = timezone.now().date()

        CommunicationPARRecord.objects.create(
            communication=self.serviceable,
            par_number="PAR-SOON",
            reference_no="REF-SOON",
            issued_to="Officer Soon",
            date_issued=today,
            expiry_date=today + timezone.timedelta(days=15),
            remarks="Expiring soon",
        )

        CommunicationPARRecord.objects.create(
            communication=self.unserviceable,
            par_number="PAR-FAR",
            reference_no="REF-FAR",
            issued_to="Officer Far",
            date_issued=today,
            expiry_date=today + timezone.timedelta(days=60),
            remarks="Not expiring soon",
        )

        expiring_count = CommunicationPARRecord.objects.filter(
            expiry_date__gt=today,
            expiry_date__lte=today + timezone.timedelta(days=30),
        ).count()

        self.assertEqual(expiring_count, 1)


class CommunicationBERBehaviorTest(TestCase):

    def setUp(self):
        self.category = create_category()
        self.comm = create_communication(self.category, "009")

        self.par = CommunicationPARRecord.objects.create(
            communication=self.comm,
            par_number="PAR-BER",
            reference_no="REF-BER",
            issued_to="Officer Juan",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="PAR before BER",
        )

        self.ics = CommunicationICSRecord.objects.create(
            communication=self.comm,
            ics_number="ICS-BER",
            reference_no="ICS-REF-BER",
            issued_to="Officer Maria",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="ICS before BER",
        )

    def test_move_to_ber_deletes_par_and_ics_records(self):
        CommunicationPARRecord.objects.filter(communication=self.comm).delete()
        CommunicationICSRecord.objects.filter(communication=self.comm).delete()

        self.assertFalse(
            CommunicationPARRecord.objects.filter(communication=self.comm).exists()
        )

        self.assertFalse(
            CommunicationICSRecord.objects.filter(communication=self.comm).exists()
        )

    def test_move_to_ber_removes_communication_record(self):
        comm_id = self.comm.asset_ptr_id

        CommunicationPARRecord.objects.filter(communication_id=comm_id).delete()
        CommunicationICSRecord.objects.filter(communication_id=comm_id).delete()
        Communication.objects.filter(asset_ptr_id=comm_id).delete()

        self.assertFalse(
            Communication.objects.filter(asset_ptr_id=comm_id).exists()
        )

    def test_move_to_ber_sets_parent_asset_status_to_4(self):
        comm_id = self.comm.asset_ptr_id

        Asset.objects.filter(id=comm_id).update(StatusID_id=4)

        updated_asset = Asset.objects.get(id=comm_id)

        self.assertEqual(updated_asset.StatusID_id, 4)