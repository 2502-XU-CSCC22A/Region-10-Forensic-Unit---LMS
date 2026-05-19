from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from config.models import Category, AssetStatus
from .forms import VehicleForm, PARForm
from .models import Vehicle, PARRecord, ActivityLog


def create_category():
    return Category.objects.get_or_create(category_name="VEHICLE")[0]


def create_status(status_id, status_name):
    return AssetStatus.objects.get_or_create(
        status_id=status_id,
        defaults={"status_name": status_name},
    )[0]


def setup_required_data():
    create_category()
    create_status(4, "BER")
    create_status(5, "Disposed")
    create_status(6, "Serviceable")
    create_status(7, "Unserviceable")


def create_vehicle(
    vehicle_id="VEH-001",
    plate_number="ABC-1234",
    status="Serviceable",
):
    setup_required_data()

    return Vehicle.objects.create(
        vehicle_id=vehicle_id,
        plate_number=plate_number,
        primary_driver="Ben Dizon",
        alternative_driver="Kate Almonte",
        classification="SUV",
        make_model="Toyota Hilux",
        year="2026",
        conduction_number="COND-001",
        status=status,
        engine_number=f"ENG-{vehicle_id}",
        chassis_number=f"CHS-{vehicle_id}",
        registration_renewal_date=timezone.now().date() + timedelta(days=60),
        insurance_renewal_date=timezone.now().date() + timedelta(days=60),
    )


class VehicleModelTest(TestCase):

    def test_vehicle_string_output(self):
        vehicle = create_vehicle()

        self.assertIn("Toyota Hilux", str(vehicle))
        self.assertIn("ABC-1234", str(vehicle))

    def test_vehicle_creates_linked_asset(self):
        vehicle = create_vehicle()

        self.assertIsNotNone(vehicle.asset)
        self.assertEqual(vehicle.asset.model, "Toyota Hilux")
        self.assertEqual(vehicle.asset.category.category_name, "VEHICLE")

    def test_vehicle_status_updates_asset_status(self):
        vehicle = create_vehicle(status="Serviceable")

        vehicle.status = "Unserviceable"
        vehicle.save()

        vehicle.asset.refresh_from_db()

        self.assertEqual(vehicle.asset.status.status_name, "Unserviceable")


class VehicleFormTest(TestCase):

    def test_vehicle_form_is_valid(self):
        setup_required_data()

        form = VehicleForm(
            data={
                "vehicle_id": "VEH-002",
                "plate_number": "XYZ-5678",
                "primary_driver": "Ben Dizon",
                "alternative_driver": "Kate Almonte",
                "classification": "SUV",
                "make_model": "Ford Everest",
                "year": "2025",
                "conduction_number": "COND-002",
                "status": "Serviceable",
                "engine_number": "ENG-002",
                "chassis_number": "CHS-002",
                "registration_renewal_date": timezone.now().date(),
                "insurance_renewal_date": timezone.now().date(),
            }
        )

        self.assertTrue(form.is_valid())

    def test_vehicle_form_invalid_without_make_model(self):
        setup_required_data()

        form = VehicleForm(
            data={
                "vehicle_id": "VEH-003",
                "plate_number": "MISS-001",
                "classification": "SUV",
                "make_model": "",
                "status": "Serviceable",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("make_model", form.errors)

    def test_vehicle_form_status_choices_exclude_disposed(self):
        form = VehicleForm()

        status_values = [choice[0] for choice in form.fields["status"].choices]

        self.assertIn("Serviceable", status_values)
        self.assertIn("Unserviceable", status_values)
        self.assertIn("BER", status_values)
        self.assertNotIn("Disposed", status_values)


class MobilityPARTest(TestCase):

    def setUp(self):
        self.vehicle = create_vehicle()

        self.par = PARRecord.objects.create(
            vehicle=self.vehicle,
            par_number="PAR-2026-001",
            issued_to="Ben",
            date_acquired=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=20),
            remarks="Test PAR",
        )

    def test_par_string_output(self):
        self.assertEqual(str(self.par), "PAR-2026-001 - Ben")

    def test_duplicate_par_number_is_invalid(self):
        form = PARForm(
            data={
                "vehicle": self.vehicle.id,
                "par_number": "PAR-2026-001",
                "issued_to": "Kate",
                "date_acquired": timezone.now().date(),
                "expiry_date": timezone.now().date() + timedelta(days=30),
                "remarks": "Duplicate PAR",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("par_number", form.errors)

    def test_new_par_form_is_valid(self):
        vehicle = create_vehicle(
            vehicle_id="VEH-004",
            plate_number="NEW-4444",
        )

        form = PARForm(
            data={
                "vehicle": vehicle.id,
                "par_number": "PAR-2026-002",
                "issued_to": "David James",
                "date_acquired": timezone.now().date(),
                "expiry_date": timezone.now().date() + timedelta(days=30),
                "remarks": "Valid PAR",
            }
        )

        self.assertTrue(form.is_valid())

    def test_expiring_par_detected(self):
        today = timezone.now().date()
        upcoming_limit = today + timedelta(days=30)

        expiring = PARRecord.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=upcoming_limit,
        )

        self.assertEqual(expiring.count(), 1)


class MobilityActivityLogTest(TestCase):

    def test_activity_log_creation(self):
        ActivityLog.objects.create(
            action_type="CREATE",
            description="Created mobility vehicle",
        )

        self.assertEqual(ActivityLog.objects.count(), 1)
