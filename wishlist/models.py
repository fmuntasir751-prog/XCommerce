from django.conf import settings
from django.db import models

from products.models import Product


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="wishlist_items",
        on_delete=models.CASCADE,
    )

    product = models.ForeignKey(
        Product,
        related_name="wishlisted_by",
        on_delete=models.CASCADE,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_wishlist_product",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"