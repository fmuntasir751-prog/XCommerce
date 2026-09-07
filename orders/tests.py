from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product

from .models import Order, OrderItem


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="buyer",
            first_name="Fahim",
            last_name="Muntasir",
            email="buyer@example.com",
            password="StrongPass123!",
        )

        category = Category.objects.create(
            name="Fashion",
            slug="fashion",
        )

        self.product = Product.objects.create(
            category=category,
            name="Premium T-Shirt",
            slug="premium-t-shirt",
            description="Test t-shirt",
            price=2999,
            discount_price=2499,
            stock=10,
            is_available=True,
        )

    def add_product_to_session_cart(self):
        session = self.client.session

        session["cart"] = {
            str(self.product.id): {
                "quantity": 2,
                "price": "2499.00",
            }
        }

        session.save()

    def test_checkout_requires_login(self):
        self.add_product_to_session_cart()

        response = self.client.get(
            reverse("orders:checkout")
        )

        expected_url = (
            reverse("accounts:login")
            + "?next="
            + reverse("orders:checkout")
        )

        self.assertRedirects(
            response,
            expected_url,
        )

    def test_customer_can_place_order(self):
        self.client.force_login(self.user)
        self.add_product_to_session_cart()

        response = self.client.post(
            reverse("orders:checkout"),
            {
                "full_name": "Fahim Muntasir",
                "email": "buyer@example.com",
                "phone": "08012345678",
                "postal_code": "533-0000",
                "city": "Osaka",
                "address": "Higashiyodogawa, Osaka",
                "payment_method": "cod",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

        order = Order.objects.first()

        self.assertEqual(
            order.total_price,
            4998,
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            8,
        )

        self.assertNotIn(
            "cart",
            self.client.session,
        )