from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class AccountTests(TestCase):
    def test_customer_registration(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newcustomer",
                "first_name": "Fahim",
                "last_name": "Muntasir",
                "email": "customer@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(
            username="newcustomer"
        )

        self.assertTrue(
            Profile.objects.filter(user=user).exists()
        )

    def test_profile_requires_login(self):
        response = self.client.get(
            reverse("accounts:profile")
        )

        expected_login_url = (
            reverse("accounts:login")
            + "?next="
            + reverse("accounts:profile")
        )

        self.assertRedirects(
            response,
            expected_login_url,
        )

    def test_logged_in_customer_can_view_profile(self):
        user = User.objects.create_user(
            username="customer",
            password="StrongPass123!",
        )

        Profile.objects.create(user=user)
        self.client.force_login(user)

        response = self.client.get(
            reverse("accounts:profile")
        )

        self.assertEqual(response.status_code, 200)