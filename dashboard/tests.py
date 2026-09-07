from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def test_normal_customer_cannot_open_dashboard(self):
        user = User.objects.create_user(
            username="customer",
            password="StrongPass123!",
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("dashboard:dashboard_home")
        )

        self.assertNotEqual(response.status_code, 200)

    def test_staff_can_open_dashboard(self):
        staff_user = User.objects.create_user(
            username="staffuser",
            password="StrongPass123!",
            is_staff=True,
        )

        self.client.force_login(staff_user)

        response = self.client.get(
            reverse("dashboard:dashboard_home")
        )

        self.assertEqual(response.status_code, 200)