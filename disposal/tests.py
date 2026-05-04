from django.test import TestCase
from django.utils import timezone
from config.models import Asset, AssetStatus
from mobility.models import Vehicle
from .models import DisposalItem, DisposalActivityLog


class DisposalWorkflowTest(TestCase):
    def setUp(self):
       
        self.active_status = AssetStatus.objects.create(Status_Name="Active")
        self.ber_status = AssetStatus.objects.create(Status_Name="BER")
        self.disposed_status = AssetStatus.objects.create(Status_Name="Disposed")

        self.asset = Asset.objects.create(
            property_no="PN-2026-XYZ",
            serial_no="SN-9999",
            model="Toyota Hilux",
            StatusID=self.active_status
        )

        self.vehicle = Vehicle.objects.create(
            asset=self.asset,
            make="Toyota",
            model="Hilux",
            plate_number="ABC-1234",
            status="Operational",
            odometer_reading=50000
        )

    def test_complete_disposal_flow(self):
        self.asset.StatusID = self.ber_status
        self.asset.save()
        
        self.vehicle.status = "For Disposal"
        self.vehicle.save()

        self.assertEqual(Asset.objects.get(id=self.asset.id).StatusID.Status_Name, "BER")

        disposal_entry = DisposalItem.objects.create(
            asset_ptr=self.asset, 
            days_overdue=0,
            disposal_reason="Engine failure - Beyond Economic Repair",
            disposal_date=timezone.now()
        )

        self.asset.StatusID = self.disposed_status
        self.asset.save()

        asset_check = Asset.objects.filter(property_no="PN-2026-XYZ").exists()
        self.assertTrue(asset_check, "Database record was accidentally deleted!")

        archived_item = DisposalItem.objects.get(asset_ptr_id=self.asset.id)
        self.assertEqual(archived_item.disposal_reason, "Engine failure - Beyond Economic Repair")

        log_exists = DisposalActivityLog.objects.filter(asset=self.asset).exists()
        self.assertTrue(log_exists, "No audit trail found in DisposalActivityLog")

    def test_disposal_archive_persistence(self):
        DisposalItem.objects.create(
            asset_ptr=self.asset,
            disposal_reason="Expired",
            disposal_date=timezone.now(),
            days_overdue=10
        )

        self.vehicle.delete()

        self.assertTrue(Asset.objects.filter(id=self.asset.id).exists())
        self.assertTrue(DisposalItem.objects.filter(asset_ptr_id=self.asset.id).exists())