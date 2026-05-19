import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .models import UserProfile


def set_role(user, role):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = role
    profile.save()
    return profile


class UserProfileModelTest(TestCase):

    def test_profile_string_output(self):
        user = User.objects.create_user(username="ben", password="testpass123")
        profile = set_role(user, "Admin")

        self.assertEqual(str(profile), "ben")

    def test_user_profile_can_store_role_and_avatar(self):
        user = User.objects.create_user(username="kate", password="testpass123")

        profile = set_role(user, "User")
        profile.avatar = "https://example.com/avatar.png"
        profile.save()

        self.assertEqual(profile.role, "User")
        self.assertEqual(profile.avatar, "https://example.com/avatar.png")


class UserManagementViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(
            username="admin",
            password="admin123",
            email="admin@test.com",
            first_name="Admin",
            last_name="User",
        )
        set_role(self.admin, "Admin")

        self.normal_user = User.objects.create_user(
            username="normal",
            password="user123",
            email="normal@test.com",
            first_name="Normal",
            last_name="User",
        )
        set_role(self.normal_user, "User")

    def test_user_list_requires_login(self):
        response = self.client.get(reverse("user_management:user_list"))

        self.assertEqual(response.status_code, 302)

    def test_user_list_loads_for_logged_in_user(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.get(reverse("user_management:user_list"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.context)

    def test_user_list_context_contains_current_user_role(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.get(reverse("user_management:user_list"))

        self.assertEqual(response.context["current_user_role"], "Admin")

    def test_user_list_only_shows_active_users(self):
        inactive = User.objects.create_user(
            username="inactive",
            password="inactive123",
            email="inactive@test.com",
            is_active=False,
        )
        set_role(inactive, "User")

        self.client.login(username="admin", password="admin123")

        response = self.client.get(reverse("user_management:user_list"))

        users = list(response.context["users"])

        self.assertIn(self.admin, users)
        self.assertIn(self.normal_user, users)
        self.assertNotIn(inactive, users)


class UpdateUserRoleTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(username="admin", password="admin123")
        set_role(self.admin, "Admin")

        self.normal_user = User.objects.create_user(
            username="normal", password="user123"
        )
        set_role(self.normal_user, "User")

        self.target_user = User.objects.create_user(
            username="target", password="target123"
        )
        set_role(self.target_user, "User")

    def test_admin_can_update_user_role(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.post(
            reverse("user_management:update_user_role", args=[self.target_user.id]),
            data=json.dumps({"role": "Admin"}),
            content_type="application/json",
        )

        self.target_user.userprofile.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(self.target_user.userprofile.role, "Admin")

    def test_non_admin_cannot_update_user_role(self):
        self.client.login(username="normal", password="user123")

        response = self.client.post(
            reverse("user_management:update_user_role", args=[self.target_user.id]),
            data=json.dumps({"role": "Admin"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])

    def test_invalid_role_is_rejected(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.post(
            reverse("user_management:update_user_role", args=[self.target_user.id]),
            data=json.dumps({"role": "SuperUser"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_update_role_user_not_found(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.post(
            reverse("user_management:update_user_role", args=[9999]),
            data=json.dumps({"role": "Admin"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])


class UpdateUserInfoTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.admin = User.objects.create_user(username="admin", password="admin123")
        set_role(self.admin, "Admin")

        self.normal_user = User.objects.create_user(
            username="normal", password="user123"
        )
        set_role(self.normal_user, "User")

        self.target_user = User.objects.create_user(
            username="target",
            password="target123",
            email="target@test.com",
            first_name="Old",
            last_name="Name",
        )
        set_role(self.target_user, "User")

        self.existing_email_user = User.objects.create_user(
            username="existing",
            password="existing123",
            email="existing@test.com",
        )
        set_role(self.existing_email_user, "User")

    def test_admin_can_update_user_info(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.post(
            reverse("user_management:update_user", args=[self.target_user.id]),
            data=json.dumps(
                {
                    "first_name": "Ben",
                    "last_name": "Dizon",
                    "email": "ben@test.com",
                }
            ),
            content_type="application/json",
        )

        self.target_user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(self.target_user.first_name, "Ben")
        self.assertEqual(self.target_user.last_name, "Dizon")
        self.assertEqual(self.target_user.email, "ben@test.com")

    def test_non_admin_cannot_update_user_info(self):
        self.client.login(username="normal", password="user123")

        response = self.client.post(
            reverse("user_management:update_user", args=[self.target_user.id]),
            data=json.dumps(
                {
                    "first_name": "Ben",
                    "last_name": "Dizon",
                    "email": "ben@test.com",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["success"])

    def test_missing_first_name_is_rejected(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.post(
            reverse("user_management:update_user", args=[self.target_user.id]),
            data=json.dumps(
                {
                    "first_name": "",
                    "last_name": "Dizon",
                    "email": "ben@test.com",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_missing_email_is_rejected(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.post(
            reverse("user_management:update_user", args=[self.target_user.id]),
            data=json.dumps(
                {
                    "first_name": "Ben",
                    "last_name": "Dizon",
                    "email": "",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_duplicate_email_is_rejected(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.post(
            reverse("user_management:update_user", args=[self.target_user.id]),
            data=json.dumps(
                {
                    "first_name": "Ben",
                    "last_name": "Dizon",
                    "email": "existing@test.com",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.json()["success"])

    def test_update_user_not_found(self):
        self.client.login(username="admin", password="admin123")

        response = self.client.post(
            reverse("user_management:update_user", args=[9999]),
            data=json.dumps(
                {
                    "first_name": "Ben",
                    "last_name": "Dizon",
                    "email": "ben@test.com",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json()["success"])
