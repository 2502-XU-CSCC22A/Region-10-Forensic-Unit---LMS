from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Vehicle
from datetime import timedelta, date

class VehicleModelTests(TestCase):
    """
    Test Suite for Vehicle model functionality.
    """

    def test_vehicle_creation(self):
        """Test that a vehicle can be created successfully"""
        vehicle = Vehicle.objects.create(
            vehicle_id="V001",
            model="Toyota Corolla",
            year=2020,
            status="Available"
        )
        self.assertEqual(vehicle.model, "Toyota Corolla")
        self.assertEqual(vehicle.year, 2020)
        self.assertEqual(vehicle.status, "Available")
        self.assertEqual(str(vehicle), "Toyota Corolla (V001)")

    def test_vehicle_id_unique(self):
        """Test that the vehicle ID is unique"""
        vehicle1 = Vehicle.objects.create(
            vehicle_id="V001", model="Toyota Corolla", year=2020, status="Available"
        )
        with self.assertRaises(IntegrityError):  # Corrected to IntegrityError
            vehicle2 = Vehicle.objects.create(
                vehicle_id="V001", model="Honda Civic", year=2021, status="In Use"
            )

    def test_registration_renewal_date_validation(self):
        """Test that the registration renewal date cannot be in the past"""
        vehicle = Vehicle(
            vehicle_id="V002",
            model="Honda Civic",
            year=2021,
            status="Available",
            registration_renewal_date=date.today() - timedelta(days=1)  # Use date.today() for the comparison
        )
        with self.assertRaises(ValidationError):
            vehicle.full_clean()  # This will call the `clean()` method and trigger validation

    def test_create_vehicle_with_future_renewal_dates(self):
        """Test that the vehicle is valid with future renewal dates"""
        vehicle = Vehicle.objects.create(
            vehicle_id="V003",
            model="Ford Mustang",
            year=2022,
            status="In Use",
            registration_renewal_date=date.today() + timedelta(days=30),  # future date
            insurance_renewal_date=date.today() + timedelta(days=60)  # future date
        )
        self.assertEqual(vehicle.registration_renewal_date.day, (date.today() + timedelta(days=30)).day)
        self.assertEqual(vehicle.insurance_renewal_date.day, (date.today() + timedelta(days=60)).day)

    def test_vehicle_deletion(self):
        """Test that a vehicle can be deleted successfully"""
        vehicle = Vehicle.objects.create(
            vehicle_id="V004", model="Chevrolet Malibu", year=2020, status="Available"
        )
        vehicle_count_before = Vehicle.objects.count()
        vehicle.delete()
        vehicle_count_after = Vehicle.objects.count()
        self.assertEqual(vehicle_count_after, vehicle_count_before - 1)
        
        # Check if the vehicle has been deleted
        with self.assertRaises(Vehicle.DoesNotExist):
            Vehicle.objects.get(vehicle_id="V004")

    def test_vehicle_status_update(self):
        """Test that a vehicle's status can be updated successfully"""
        vehicle = Vehicle.objects.create(
            vehicle_id="V005", model="Nissan Altima", year=2021, status="Available"
        )
        vehicle.status = "In Use"
        vehicle.save()
        updated_vehicle = Vehicle.objects.get(vehicle_id="V005")
        self.assertEqual(updated_vehicle.status, "In Use")