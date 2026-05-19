from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from config.models import Asset, AssetStatus, Category

User = get_user_model()


def create_status():
    return AssetStatus.objects.get_or_create(
        status_id=1, defaults={"status_name": "Available"}
    )[0]


def create_category():
    return Category.objects.get_or_create(category_name="Communications")[0]


def create_asset():

    status = create_status()

    category = create_category()

    return Asset.objects.create(
        property_no="PROP-001",
        serial_no="SERIAL-001",
        model="Radio Device",
        quantity="1",
        category=category,
        status=status,
        date_acquired=timezone.now().date(),
    )


class DashboardAccessTests(TestCase):

    def setUp(self):

        self.client = Client()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.asset = create_asset()

    def test_redirect_when_not_logged_in(self):

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads_for_authenticated_user(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertTemplateUsed(response, "dashboard/dashboard.html")

    def test_dashboard_context_contains_total_assets(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertIn("total_assets", response.context)

    def test_dashboard_context_contains_total_firearms(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertIn("total_firearms", response.context)

    def test_dashboard_context_contains_total_mobility(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertIn("total_mobility", response.context)

    def test_dashboard_context_contains_total_communications(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertIn("total_communications", response.context)

    def test_dashboard_context_contains_total_investigative(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertIn("total_investigative", response.context)

    def test_dashboard_context_contains_notification_count(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertIn("notification_count", response.context)

    def test_dashboard_context_contains_activities(self):

        self.client.login(
            username="testuser",
            password="testpassword123",
        )

        response = self.client.get(reverse("dashboard:dashboard_view"))

        self.assertIn("activities", response.context)

        self.assertIsInstance(response.context["activities"], list)


class DashboardActivityTests(TestCase):

    def setUp(self):

        self.client = Client()

        self.user = User.objects.create_user(
            username="admin", password="admin123", is_staff=True
        )

        self.asset = create_asset()

    def test_dashboard_generates_activity_logs(self):

        content_type = ContentType.objects.get_for_model(Asset)

        LogEntry.objects.create(
            user=self.user,
            content_type=content_type,
            object_id=self.asset.id,
            object_repr=str(self.asset),
            action_flag=ADDITION,
            change_message="Added asset",
        )

        self.client.login(username="admin", password="admin123")

        response = self.client.get(reverse("dashboard:dashboard_view"))

        activities = response.context["activities"]

        self.assertGreater(len(activities), 0)

    def test_mark_all_read_endpoint(self):

        self.client.login(username="admin", password="admin123")

        response = self.client.post(reverse("dashboard:mark_all_read"))

        self.assertEqual(response.status_code, 200)

    def test_mark_all_read_returns_json(self):

        self.client.login(username="admin", password="admin123")

        response = self.client.post(reverse("dashboard:mark_all_read"))

        self.assertEqual(response.json()["status"], "ok")
