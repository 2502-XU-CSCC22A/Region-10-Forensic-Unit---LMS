from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
        )

    # Unauthenticated 

    def test_redirect_when_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(
            response,
            f"/login/?next={reverse('dashboard')}",
            fetch_redirect_response=False,
        )

    # Authenticated

    def test_dashboard_loads_for_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'Dashboard/dashboard.html')

    def test_context_contains_total_assets(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn('total_assets', response.context)

    def test_context_contains_total_categories(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn('total_categories', response.context)

    def test_context_contains_status_counts(self):
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn('status_counts', response.context)
        self.assertIsInstance(response.context['status_counts'], dict)