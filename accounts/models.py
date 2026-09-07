from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    address = models.TextField(blank=True)

    avatar = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.username}'s profile"