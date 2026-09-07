from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from.models import Profile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
    )

    email = forms.EmailField(required=True)

    class Meta:
        model = User

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email
    from .models import Profile


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User

        fields = (
            "first_name",
            "last_name",
            "email",
        )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile

        fields = (
            "phone",
            "postal_code",
            "city",
            "address",
            "avatar",
        )

        widgets = {
            "address": forms.Textarea(
                attrs={"rows": 4}
            ),
        }