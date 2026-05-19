from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import LoginToken


class LoginTokenModelTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username="ben", password="testpass123")

    def test_generate_token_creates_token(self):

        token = LoginToken.generate(self.user)

        self.assertTrue(LoginToken.objects.filter(token=token).exists())

    def test_generate_token_removes_old_tokens(self):

        old_token = LoginToken.generate(self.user)

        LoginToken.generate(self.user)

        self.assertFalse(LoginToken.objects.filter(token=old_token).exists())

    def test_consume_valid_token_returns_user(self):

        token = LoginToken.generate(self.user)

        consumed_user = LoginToken.consume(token)

        self.assertEqual(consumed_user, self.user)

    def test_consume_deletes_token_after_use(self):

        token = LoginToken.generate(self.user)

        LoginToken.consume(token)

        self.assertFalse(LoginToken.objects.filter(token=token).exists())

    def test_consume_invalid_token_returns_none(self):

        result = LoginToken.consume("invalid-token")

        self.assertIsNone(result)

    def test_expired_token_returns_none(self):

        token = LoginToken.generate(self.user)

        token_obj = LoginToken.objects.get(token=token)

        token_obj.expires_at = timezone.now() - timedelta(minutes=30)

        token_obj.save()

        result = LoginToken.consume(token)

        self.assertIsNone(result)


class LoginViewTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username="ben", password="testpass123")

    def test_login_page_loads(self):

        response = self.client.get(reverse("login:login"))

        self.assertEqual(response.status_code, 200)

    def test_valid_login_generates_token(self):

        response = self.client.post(
            reverse("login:login"),
            {
                "username": "ben",
                "password": "testpass123",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(LoginToken.objects.count(), 1)

    def test_invalid_login_does_not_generate_token(self):

        response = self.client.post(
            reverse("login:login"),
            {
                "username": "ben",
                "password": "wrongpassword",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(LoginToken.objects.count(), 0)

    def test_authenticated_user_redirected_from_login(self):

        self.client.login(username="ben", password="testpass123")

        response = self.client.get(reverse("login:login"))

        self.assertEqual(response.status_code, 302)


class VerifyTokenViewTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username="ben", password="testpass123")

    def test_valid_token_logs_user_in(self):

        token = LoginToken.generate(self.user)

        response = self.client.get(reverse("login:verify_token", args=[token]))

        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("login:dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_invalid_token_redirects_to_login(self):

        response = self.client.get(
            reverse("login:verify_token", args=["invalid-token"])
        )

        self.assertEqual(response.status_code, 302)

    def test_expired_token_redirects_to_login(self):

        token = LoginToken.generate(self.user)

        token_obj = LoginToken.objects.get(token=token)

        token_obj.expires_at = timezone.now() - timedelta(minutes=30)

        token_obj.save()

        response = self.client.get(reverse("login:verify_token", args=[token]))

        self.assertEqual(response.status_code, 302)


class LogoutViewTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username="ben", password="testpass123")

    def test_logout_redirects_user(self):

        self.client.login(username="ben", password="testpass123")

        response = self.client.get(reverse("login:logout"))

        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_login(self):

        response = self.client.get(reverse("login:dashboard"))

        self.assertEqual(response.status_code, 302)
