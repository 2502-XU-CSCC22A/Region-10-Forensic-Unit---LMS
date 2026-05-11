from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from .models import Vehicle, PARRecord, ActivityLog


class MobilityBaseTest(TestCase):

    def setUp(self):
        self.client = Client()

        # Admin User
        self.admin_user = User.objects.create_user(
            username='Admin',
            password='Admin_102026'
        )

        # Logistics Officer User
        self.logistics_user = User.objects.create_user(
            username='logistics',
            password='logistics123'
        )

        # Supervisor User (Read-only)
        self.supervisor_user = User.objects.create_user(
            username='supervisor',
            password='supervisor123'
        )

        # Test Vehicle
        self.vehicle = Vehicle.objects.create(
            vehicle_id='VH-001',
            plate_number='ABC-1234',
            classification='SUV',
            make_model='Toyota Fortuner',
            primary_driver='Juan Dela Cruz',
            status='Serviceable'
        )

        # Test PAR
        self.par = PARRecord.objects.create(
            vehicle=self.vehicle,
            par_number='PAR-001',
            issued_to='John Doe',
            date_acquired=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=20),
            remarks='Test PAR'
        )


# =========================================================
# VEHICLE MANAGEMENT TESTS
# =========================================================

class VehicleManagementTests(MobilityBaseTest):

    def test_vehicle_management_page_loads(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.get(
            reverse('mobility:vehicle_management')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vehicle Management Registry')


# =========================================================
# VEHICLE CREATION TESTS
# =========================================================

class VehicleCreationTests(MobilityBaseTest):

    def test_create_vehicle(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:vehicle_management'),
            {
                'vehicle_id': 'VH-002',
                'plate_number': 'XYZ-5678',
                'classification': 'SUV',
                'make_model': 'Montero Sport',
                'primary_driver': 'Pedro Santos',
                'status': 'Serviceable',
                'par_number': 'PAR-002',
                'issued_to': 'Pedro Santos',
                'date_acquired': timezone.now().date(),
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vehicle.objects.count(), 2)


# =========================================================
# SEARCH TESTS
# =========================================================

class VehicleSearchTests(MobilityBaseTest):

    def test_search_vehicle(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.get(
            reverse('mobility:vehicle_management'),
            {
                'plate_no': 'ABC-1234'
            }
        )

        self.assertContains(response, 'Toyota Fortuner')


# =========================================================
# DELETE TESTS
# =========================================================

class VehicleDeleteTests(MobilityBaseTest):

    def test_delete_vehicle(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:delete_vehicle', args=[self.vehicle.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vehicle.objects.count(), 0)


# =========================================================
# BER WORKFLOW TESTS
# =========================================================

class BERWorkflowTests(MobilityBaseTest):

    def test_mark_vehicle_ber(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:mark_vehicle_ber', args=[self.vehicle.id])
        )

        self.vehicle.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.vehicle.status, 'BER')

    def test_send_vehicle_to_disposal(self):
        self.client.login(username='Admin', password='Admin_102026')

        self.vehicle.status = 'BER'
        self.vehicle.save()

        response = self.client.post(
            reverse('mobility:send_vehicle_to_disposal', args=[self.vehicle.id])
        )

        self.vehicle.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.vehicle.status, 'Disposed')


# =========================================================
# PAR MANAGEMENT TESTS
# =========================================================

class PARManagementTests(MobilityBaseTest):

    def test_par_management_page_loads(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.get(
            reverse('mobility:par_management')
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_par(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:delete_par', args=[self.par.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PARRecord.objects.count(), 0)


# =========================================================
# ACTIVITY LOG TESTS
# =========================================================

class ActivityLogTests(MobilityBaseTest):

    def test_activity_log_creation(self):
        ActivityLog.objects.create(
            user=self.admin_user,
            action_type='CREATE',
            description='Created a vehicle'
        )

        self.assertEqual(ActivityLog.objects.count(), 1)

    def test_activity_log_page(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.get(
            reverse('mobility:activity_log')
        )

        self.assertEqual(response.status_code, 200)


# =========================================================
# PERMISSION TESTS
# =========================================================

class PermissionTests(MobilityBaseTest):

    def test_supervisor_cannot_delete_vehicle(self):
        self.client.login(username='supervisor', password='supervisor123')

        response = self.client.post(
            reverse('mobility:delete_vehicle', args=[self.vehicle.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_supervisor_cannot_mark_ber(self):
        self.client.login(username='supervisor', password='supervisor123')

        response = self.client.post(
            reverse('mobility:mark_vehicle_ber', args=[self.vehicle.id])
        )

        self.assertEqual(response.status_code, 403)


# =========================================================
# EXPIRING PAR TESTS
# =========================================================

class ExpiringPARTests(MobilityBaseTest):

    def test_expiring_par_record(self):
        upcoming_limit = timezone.now().date() + timedelta(days=30)

        expiring = PARRecord.objects.filter(
            expiry_date__gte=timezone.now().date(),
            expiry_date__lte=upcoming_limit
        )

        self.assertEqual(expiring.count(), 1)


# =========================================================
# EMAIL ALERT TESTS
# =========================================================

class EmailAlertTests(MobilityBaseTest):

    def test_urgent_vehicle_detection(self):
        self.vehicle.status = 'BER'
        self.vehicle.save()

        urgent = Vehicle.objects.filter(
            status__in=['Unserviceable', 'BER']
        )

        self.assertEqual(urgent.count(), 1)


# =========================================================
# ERROR HANDLING TESTS
# =========================================================

class MobilityErrorHandlingTests(MobilityBaseTest):

    def test_invalid_form_submission_does_not_create_vehicle(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:vehicle_management'),
            {
                'vehicle_id': '',
                'plate_number': '',
                'classification': '',
                'make_model': '',
                'status': '',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vehicle.objects.count(), 1)

    def test_duplicate_vehicle_id_not_allowed(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:vehicle_management'),
            {
                'vehicle_id': 'VH-001',
                'plate_number': 'NEW-1234',
                'classification': 'SUV',
                'make_model': 'Toyota Hilux',
                'primary_driver': 'Test Driver',
                'status': 'Serviceable',
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Vehicle.objects.filter(vehicle_id='VH-001').count(),
            1
        )

    def test_duplicate_plate_number_not_allowed(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:vehicle_management'),
            {
                'vehicle_id': 'VH-999',
                'plate_number': 'ABC-1234',
                'classification': 'SUV',
                'make_model': 'Toyota Hilux',
                'primary_driver': 'Test Driver',
                'status': 'Serviceable',
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            Vehicle.objects.filter(plate_number='ABC-1234').count(),
            1
        )

    def test_missing_required_make_model_does_not_create_vehicle(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:vehicle_management'),
            {
                'vehicle_id': 'VH-003',
                'plate_number': 'MISS-001',
                'classification': 'SUV',
                'make_model': '',
                'status': 'Serviceable',
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Vehicle.objects.filter(vehicle_id='VH-003').exists()
        )

    def test_invalid_par_data_does_not_create_par(self):
        self.client.login(username='Admin', password='Admin_102026')

        response = self.client.post(
            reverse('mobility:vehicle_management'),
            {
                'vehicle_id': 'VH-004',
                'plate_number': 'PAR-404',
                'classification': 'SUV',
                'make_model': 'Toyota Hilux',
                'status': 'Serviceable',
                'par_number': 'PAR-BAD',
                'issued_to': '',
                'date_acquired': 'invalid-date',
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            PARRecord.objects.filter(par_number='PAR-BAD').exists()
        )

    def test_unauthenticated_user_redirected_from_vehicle_management(self):
        response = self.client.get(
            reverse('mobility:vehicle_management')
        )

        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_user_redirected_from_par_management(self):
        response = self.client.get(
            reverse('mobility:par_management')
        )

        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_user_redirected_from_activity_log(self):
        response = self.client.get(
            reverse('mobility:activity_log')
        )

        self.assertEqual(response.status_code, 302)

    @patch('smtplib.SMTP')
    def test_email_sending_failure_handled(self, mock_smtp):
        self.client.login(username='Admin', password='Admin_102026')

        self.vehicle.status = 'BER'
        self.vehicle.save()

        mock_smtp.return_value.__enter__.return_value.login.side_effect = Exception(
            'SMTP failed'
        )

        response = self.client.get(
            reverse('mobility:manual_email_alert')
        )

        self.assertEqual(response.status_code, 302)