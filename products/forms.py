from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review

        fields = (
            "rating",
            "comment",
        )

        widgets = {
            "rating": forms.Select(
                choices=[
                    (5, "★★★★★ - Excellent"),
                    (4, "★★★★☆ - Very Good"),
                    (3, "★★★☆☆ - Good"),
                    (2, "★★☆☆☆ - Fair"),
                    (1, "★☆☆☆☆ - Poor"),
                ]
            ),

            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Write your experience with this product...",
                }
            ),
        }