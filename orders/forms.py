from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order

        fields = (
            "full_name",
            "email",
            "phone",
            "postal_code",
            "city",
            "address",
            "payment_method",
        )

        widgets = {
            "address": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Building, street and apartment",
                }
            ),
        }