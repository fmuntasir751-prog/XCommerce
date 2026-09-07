from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Review


class ProductTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testcustomer",
            password="StrongPass123!",
        )

        self.category = Category.objects.create(
            name="Electronics",
            slug="electronics",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Wireless Headphones",
            slug="wireless-headphones",
            description="Test headphones",
            price=7999,
            discount_price=6499,
            stock=10,
            is_available=True,
            is_featured=True,
        )

    def test_product_list_page(self):
        response = self.client.get(
            reverse("products:product_list")
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "Wireless Headphones",
        )

    def test_product_detail_page(self):
        response = self.client.get(
            self.product.get_absolute_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_search(self):
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Wireless"},
        )

        self.assertContains(
            response,
            "Wireless Headphones",
        )

    def test_category_filter(self):
        response = self.client.get(
            reverse(
                "products:category_products",
                kwargs={
                    "category_slug": self.category.slug,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_customer_can_add_review(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "products:add_review",
                kwargs={"product_id": self.product.id},
            ),
            {
                "rating": 5,
                "comment": "Excellent product.",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Review.objects.filter(
                user=self.user,
                product=self.product,
                rating=5,
            ).exists()
        )