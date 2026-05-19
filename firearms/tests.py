from django.test import TestCase
from django.utils import timezone

from config.models import Category, AssetStatus
from .forms import FirearmsPARForm
from .models import Firearm, FirearmPARRecord


def create_category():
    return Category.objects.get_or_create(category_name="Firearms")[0]


def create_status(status_id=1, status_name="Available"):
    return AssetStatus.objects.get_or_create(
        status_id=status_id, defaults={"status_name": status_name}
    )[0]


def create_firearm(
    property_no="PROP-FIREARM-001",
    serial_no="SFA20324",
    status_id=1,
    status_name="Available",
    validated="VALIDATED",
):

    category = create_category()

    status = create_status(status_id, status_name)

    return Firearm.objects.create(
        type="GLOCK 19 / PISTOL / 9MM",
        caliber="9MM",
        faid_serial=serial_no,
        assigned_to="PRECIOUS PAGUTE",
        unit="RFU 10",
        subunit="CRIME LAB",
        station="MALAYBALAY CITY",
        issuing_unit="PNP FG",
        validated=validated,
        date_acquired=timezone.now().date(),
        property_no=property_no,
        serial_no=serial_no,
        model="GLOCK 19",
        category=category,
        status=status,
        quantity=1,
    )


class FirearmModelTest(TestCase):

    def test_firearm_string_output(self):

        firearm = create_firearm()

        self.assertIn(firearm.assigned_to, str(firearm))

    def test_firearm_validated_default(self):

        firearm = create_firearm()

        self.assertEqual(firearm.validated, "VALIDATED")


class FirearmsPARFormTest(TestCase):

    def setUp(self):

        self.firearm = create_firearm()

        self.par = FirearmPARRecord.objects.create(
            firearm=self.firearm,
            par_number="PAR-2026-001",
            fund_cluster="FUND-001",
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
                "fund_cluster": "FUND-NEW",
                "reference_no": "REF-NEW",
                "issued_to": "Officer Pedro",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate PAR",
            }
        )

        duplicate_exists = FirearmPARRecord.objects.filter(
            par_number="PAR-2026-001"
        ).exists()

        self.assertTrue(duplicate_exists)

    def test_duplicate_reference_no_is_invalid(self):

        form = FirearmsPARForm(
            data={
                "firearm": self.firearm.asset_ptr_id,
                "par_number": "PAR-NEW",
                "fund_cluster": "FUND-NEW",
                "reference_no": "REF-001",
                "issued_to": "Officer Pedro",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate REF",
            }
        )

        duplicate_exists = FirearmPARRecord.objects.filter(
            reference_no="REF-001"
        ).exists()

        self.assertTrue(duplicate_exists)

    def test_used_firearm_not_shown_in_par_dropdown(self):

        form = FirearmsPARForm()

        firearm_choices = [
            choice[0] for choice in form.fields["firearm"].widget.choices
        ]

        self.assertNotIn(self.firearm.asset_ptr_id, firearm_choices)

    def test_available_firearm_shown_in_dropdown(self):

        unused_firearm = create_firearm(
            property_no="PROP-FIREARM-002",
            serial_no="SFA20219",
        )

        form = FirearmsPARForm()

        firearm_choices = [
            choice[0] for choice in form.fields["firearm"].widget.choices
        ]

        self.assertIn(unused_firearm.asset_ptr_id, firearm_choices)

    def test_ber_firearm_not_shown_in_dropdown(self):

        ber_firearm = create_firearm(
            property_no="PROP-BER-001",
            serial_no="SFA-BER-001",
            status_id=4,
            status_name="BER",
        )

        form = FirearmsPARForm()

        firearm_choices = [
            choice[0] for choice in form.fields["firearm"].widget.choices
        ]

        self.assertNotIn(ber_firearm.asset_ptr_id, firearm_choices)

    def test_disposed_firearm_not_shown_in_dropdown(self):

        disposed_firearm = create_firearm(
            property_no="PROP-DISP-001",
            serial_no="SFA-DISP-001",
            status_id=5,
            status_name="Disposed",
        )

        form = FirearmsPARForm()

        firearm_choices = [
            choice[0] for choice in form.fields["firearm"].widget.choices
        ]

        self.assertNotIn(disposed_firearm.asset_ptr_id, firearm_choices)

    def test_unserviceable_firearm_not_shown_in_dropdown(self):

        unserviceable_firearm = create_firearm(
            property_no="PROP-UNSERV-001",
            serial_no="SFA-UNSERV-001",
            status_id=7,
            status_name="Unserviceable",
        )

        form = FirearmsPARForm()

        firearm_choices = [
            choice[0] for choice in form.fields["firearm"].widget.choices
        ]

        self.assertNotIn(unserviceable_firearm.asset_ptr_id, firearm_choices)

    def test_new_par_form_is_valid_for_unused_firearm(self):

        unused_firearm = create_firearm(
            property_no="PROP-FIREARM-003",
            serial_no="SFA20220",
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
