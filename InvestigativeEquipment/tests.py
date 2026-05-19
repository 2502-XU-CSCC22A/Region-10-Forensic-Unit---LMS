from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from config.models import Asset, AssetStatus, Category
from .forms import InvestigativePARForm, InvestigativeICSForm
from .models import (
    InvestigativeDetails,
    InvestigativePARRecord,
    ICSRecord,
    InvestigativeActivityLog,
)


def create_category():
    return Category.objects.get_or_create(category_name="Technical Sections")[0]


def create_status(status_id=1, status_name="Available"):
    return AssetStatus.objects.get_or_create(
        status_id=status_id,
        defaults={"status_name": status_name},
    )[0]


def create_investigative_asset(
    property_no="INV-PROP-001",
    serial_no="INV-SERIAL-001",
    model="Microscope",
    quantity="1",
    office="SOCO",
    status_id=1,
    status_name="Available",
):

    category = create_category()

    status = create_status(status_id, status_name)

    asset = Asset.objects.create(
        date_acquired=timezone.now().date(),
        property_no=property_no,
        serial_no=serial_no,
        model=model,
        category=category,
        status=status,
        quantity=quantity,
    )

    InvestigativeDetails.objects.create(
        asset_id=asset,
        item_description="Test investigative item",
        par_id=property_no,
        office=office,
    )

    return asset


class InvestigativeModelTest(TestCase):

    def test_investigative_details_string_output(self):

        asset = create_investigative_asset()

        details = InvestigativeDetails.objects.get(asset_id=asset)

        self.assertIn("Details for", str(details))

    def test_investigative_asset_keeps_quantity_and_office(self):

        asset = create_investigative_asset(quantity="5", office="DNA")

        details = InvestigativeDetails.objects.get(asset_id=asset)

        self.assertEqual(str(asset.quantity), "5")

        self.assertEqual(details.office, "DNA")


class InvestigativePARFormTest(TestCase):

    def setUp(self):

        self.asset = create_investigative_asset()

        self.par = InvestigativePARRecord.objects.create(
            asset=self.asset,
            par_number="PAR-INV-001",
            reference_no="REF-INV-001",
            issued_to="Ben",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="Test PAR",
        )

    def test_duplicate_par_number_is_invalid(self):

        form = InvestigativePARForm(
            data={
                "asset": self.asset.id,
                "par_number": "PAR-INV-001",
                "reference_no": "REF-NEW",
                "issued_to": "Juan",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate PAR number",
            }
        )

        self.assertFalse(form.is_valid())

        self.assertIn("par_number", form.errors)

    def test_duplicate_par_reference_no_is_invalid(self):

        form = InvestigativePARForm(
            data={
                "asset": self.asset.id,
                "par_number": "PAR-NEW",
                "reference_no": "REF-INV-001",
                "issued_to": "Juan",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate reference",
            }
        )

        self.assertFalse(form.is_valid())

        self.assertIn("reference_no", form.errors)

    def test_used_asset_not_shown_in_par_dropdown(self):

        form = InvestigativePARForm()

        self.assertNotIn(self.asset, form.fields["asset"].queryset)

    def test_ber_disposed_and_unserviceable_not_shown_in_par_dropdown(self):

        ber = create_investigative_asset(
            "INV-BER",
            "SER-BER",
            status_id=4,
            status_name="BER",
        )

        disposed = create_investigative_asset(
            "INV-DISP",
            "SER-DISP",
            status_id=5,
            status_name="Disposed",
        )

        unserviceable = create_investigative_asset(
            "INV-UNSERV",
            "SER-UNSERV",
            status_id=7,
            status_name="Unserviceable",
        )

        form = InvestigativePARForm()

        queryset = form.fields["asset"].queryset

        self.assertNotIn(ber, queryset)

        self.assertNotIn(disposed, queryset)

        self.assertNotIn(unserviceable, queryset)

    def test_available_asset_shown_in_par_dropdown(self):

        available = create_investigative_asset(
            "INV-AVAILABLE",
            "SER-AVAILABLE",
            status_id=1,
            status_name="Available",
        )

        form = InvestigativePARForm()

        self.assertIn(available, form.fields["asset"].queryset)


class InvestigativeICSFormTest(TestCase):

    def setUp(self):

        self.asset = create_investigative_asset(
            property_no="INV-ICS-001",
            serial_no="SER-ICS-001",
        )

        self.ics = ICSRecord.objects.create(
            asset=self.asset,
            ics_number="ICS-INV-001",
            reference_no="ICS-REF-001",
            issued_to="Ben",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="Test ICS",
        )

    def test_duplicate_ics_number_is_invalid(self):

        form = InvestigativeICSForm(
            data={
                "asset": self.asset.id,
                "ics_number": "ICS-INV-001",
                "reference_no": "ICS-REF-NEW",
                "issued_to": "Maria",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate ICS number",
            }
        )

        self.assertFalse(form.is_valid())

        self.assertIn("ics_number", form.errors)

    def test_duplicate_ics_reference_no_is_invalid(self):

        form = InvestigativeICSForm(
            data={
                "asset": self.asset.id,
                "ics_number": "ICS-NEW",
                "reference_no": "ICS-REF-001",
                "issued_to": "Maria",
                "date_issued": timezone.now().date(),
                "expiry_date": timezone.now().date(),
                "remarks": "Duplicate reference",
            }
        )

        self.assertFalse(form.is_valid())

        self.assertIn("reference_no", form.errors)

    def test_used_asset_not_shown_in_ics_dropdown(self):

        form = InvestigativeICSForm()

        self.assertNotIn(self.asset, form.fields["asset"].queryset)

    def test_ber_disposed_and_unserviceable_not_shown_in_ics_dropdown(self):

        ber = create_investigative_asset(
            "INV-BER-ICS",
            "SER-BER-ICS",
            status_id=4,
            status_name="BER",
        )

        disposed = create_investigative_asset(
            "INV-DISP-ICS",
            "SER-DISP-ICS",
            status_id=5,
            status_name="Disposed",
        )

        unserviceable = create_investigative_asset(
            "INV-UNSERV-ICS",
            "SER-UNSERV-ICS",
            status_id=7,
            status_name="Unserviceable",
        )

        form = InvestigativeICSForm()

        queryset = form.fields["asset"].queryset

        self.assertNotIn(ber, queryset)

        self.assertNotIn(disposed, queryset)

        self.assertNotIn(unserviceable, queryset)

    def test_available_asset_shown_in_ics_dropdown(self):

        available = create_investigative_asset(
            "INV-AVAILABLE-ICS",
            "SER-AVAILABLE-ICS",
            status_id=1,
            status_name="Available",
        )

        form = InvestigativeICSForm()

        self.assertIn(available, form.fields["asset"].queryset)


class InvestigativeMoveToBERTest(TestCase):

    def setUp(self):

        create_status(4, "BER")

        self.asset = create_investigative_asset(
            property_no="INV-BER-MOVE",
            serial_no="SER-BER-MOVE",
        )

        self.par = InvestigativePARRecord.objects.create(
            asset=self.asset,
            par_number="PAR-MOVE-001",
            reference_no="PAR-MOVE-REF",
            issued_to="Ben",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="PAR before BER",
        )

        self.ics = ICSRecord.objects.create(
            asset=self.asset,
            ics_number="ICS-MOVE-001",
            reference_no="ICS-MOVE-REF",
            issued_to="Ben",
            date_issued=timezone.now().date(),
            expiry_date=timezone.now().date(),
            remarks="ICS before BER",
        )

    def test_move_to_ber_updates_status_and_deletes_related_records(self):

        url = reverse(
            "InvestigativeEquipment:move_to_ber_investigative", args=[self.asset.id]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

        self.asset.refresh_from_db()

        self.assertFalse(
            InvestigativeDetails.objects.filter(asset_id=self.asset).exists()
        )

        self.assertFalse(
            InvestigativePARRecord.objects.filter(asset=self.asset).exists()
        )

        self.assertFalse(ICSRecord.objects.filter(asset=self.asset).exists())
