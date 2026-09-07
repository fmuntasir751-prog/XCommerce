from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product


class CartTests(TestCase):
    def setUp(self):
        category = Category.objects.create(
            name="Sports",
            slug="sports",
        )

        self.product = Product.objects.create(
            category=category,
            name="Professional Football",
            slug="professional-football",
            description="Test football",
            price=3999,
            stock=10,
            is_available=True,
        )

    def test_add_product_to_cart(self):
        response = self.client.post(
            reverse(
                "cart:cart_add",
                kwargs={"product_id": self.product.id},
            ),
            {"quantity": 2},
        )

        self.assertEqual(response.status_code, 302)

        cart = self.client.session["cart"]

        self.assertEqual(
            cart[str(self.product.id)]["quantity"],
            2,
        )

    def test_remove_product_from_cart(self):
        self.client.post(
            reverse(
                "cart:cart_add",
                kwargs={"product_id": self.product.id},
            ),
            {"quantity": 1},
        )

        self.client.post(
            reverse(
                "cart:cart_remove",
                kwargs={"product_id": self.product.id},
            )
        )

        cart = self.client.session["cart"]

        self.assertNotIn(
            str(self.product.id),
            cart,
        )