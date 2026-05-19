from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from config.models import Asset, AssetStatus, Category
from .models import DisposalItem, DisposalActivityLog


def create_status(status_id, status_name):
    return AssetStatus.objects.get_or_create(
        status_id=status_id,
        defaults={"status_name": status_name},
    )[0]


def create_category(category_name="communications"):
    return Category.objects.get_or_create(category_name=category_name)[0]


def create_asset(
    property_no="PROP-DISP-001",
    serial_no="SER-DISP-001",
    model="Radio",
    category_name="communications",
    status_id=4,
    status_name="BER",
):
    category = create_category(category_name)
    status = create_status(status_id, status_name)

    return Asset.objects.create(
        date_acquired=timezone.now().date(),
        property_no=property_no,
        serial_no=serial_no,
        model=model,
        category=category,
        status=status,
        quantity="1",
    )


def create_disposal_item(asset=None, reason="Marked as BER from Communications"):
    if asset is None:
        asset = create_asset()

    return DisposalItem.objects.create(
        asset_ptr=asset,
        disposal_reason=reason,
        status=asset.status,
        category=asset.category,
        date_acquired=asset.date_acquired,
        property_no=asset.property_no,
        serial_no=asset.serial_no,
        model=asset.model,
        quantity=asset.quantity,
    )


class DisposalModelTest(TestCase):

    def test_disposal_item_string_output(self):
        item = create_disposal_item()

        self.assertIn("Disposal:", str(item))
        self.assertIn("Marked as BER", str(item))

    def test_disposal_activity_log_string_output(self):
        asset = create_asset()

        log = DisposalActivityLog.objects.create(
            asset=asset,
            action_type="FLAGGED",
            description="Asset flagged for disposal",
            disposal_reason="BER",
        )

        self.assertIn("FLAGGED", str(log))


class DisposalListViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="admin",
            password="password123",
        )

        self.client.login(
            username="admin",
            password="password123",
        )

        create_status(5, "Disposed")

        self.asset = create_asset()
        self.item = create_disposal_item(self.asset)

    def test_disposal_list_page_loads(self):
        response = self.client.get(reverse("disposal:disposal_list"))

        self.assertEqual(response.status_code, 200)

    def test_disposal_list_context_contains_total_ber(self):
        response = self.client.get(reverse("disposal:disposal_list"))

        self.assertIn("total_ber", response.context)
        self.assertEqual(response.context["total_ber"], 1)

    def test_disposal_list_counts_communications_ber(self):
        response = self.client.get(reverse("disposal:disposal_list"))

        self.assertIn("comms_ber", response.context)
        self.assertEqual(response.context["comms_ber"], 1)

    def test_disposal_list_contains_ber_today_count(self):
        response = self.client.get(reverse("disposal:disposal_list"))

        self.assertIn("ber_today_count", response.context)
        self.assertEqual(response.context["ber_today_count"], 1)

    def test_history_log_page_loads(self):
        DisposalActivityLog.objects.create(
            asset=self.asset,
            action_type="FLAGGED",
            description="Asset flagged for disposal",
            disposal_reason="BER",
        )

        response = self.client.get(reverse("disposal:history_log"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.context)


class DisposalFinalizeRemovalTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username="admin",
            password="password123",
        )

        self.client.login(
            username="admin",
            password="password123",
        )

        create_status(4, "BER")
        create_status(5, "Disposed")

        self.asset = create_asset(
            property_no="PROP-FINAL-001",
            serial_no="SER-FINAL-001",
            model="Handheld Radio",
            category_name="communications",
            status_id=4,
            status_name="BER",
        )

        self.item = create_disposal_item(
            self.asset,
            reason="Marked as BER from Communications",
        )

    def test_finalize_removal_updates_asset_to_disposed(self):
        response = self.client.post(
            reverse("disposal:finalize_removal", args=[self.item.pk])
        )

        self.asset.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.asset.status.status_id, 5)

    def test_finalize_removal_creates_activity_log(self):
        self.client.post(reverse("disposal:finalize_removal", args=[self.item.pk]))

        self.assertTrue(
            DisposalActivityLog.objects.filter(
                asset=self.asset, action_type="REMOVE"
            ).exists()
        )

    def test_finalize_removal_redirects_to_history(self):
        response = self.client.post(
            reverse("disposal:finalize_removal", args=[self.item.pk])
        )

        self.assertEqual(response.url, reverse("disposal:history_log"))
