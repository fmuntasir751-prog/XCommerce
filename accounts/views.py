from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from orders.models import Order
from wishlist.models import WishlistItem

from .forms import (
    ProfileUpdateForm,
    RegisterForm,
    UserUpdateForm,
)
from .models import Profile
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

from django.contrib.auth.models import User

def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            Profile.objects.get_or_create(user=user)

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = default_token_generator.make_token(user)

            activation_path = reverse(
                "accounts:activate",
                kwargs={
                    "uidb64": uid,
                    "token": token,
                },
            )

            activation_url = request.build_absolute_uri(
                activation_path
            )

            email_body = render_to_string(
                "accounts/activation_email.html",
                {
                    "user": user,
                    "activation_url": activation_url,
                },
            )

            send_mail(
                subject="Activate your XCommerce account",
                message=email_body,
                from_email=None,
                recipient_list=[user.email],
            )

            messages.success(
                request,
                "Account created. Check your email to activate it.",
            )

            return redirect("accounts:activation_sent")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    recent_orders = Order.objects.filter(
        user=request.user
    )[:5]

    wishlist_count = WishlistItem.objects.filter(
        user=request.user
    ).count()

    context = {
        "profile": profile,
        "recent_orders": recent_orders,
        "wishlist_count": wishlist_count,
        "order_count": request.user.orders.count(),
    }

    return render(
        request,
        "accounts/profile.html",
        context,
    )


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        user_form = UserUpdateForm(
            request.POST,
            instance=request.user,
        )

        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(
                request,
                "Your profile was updated successfully.",
            )

            return redirect("accounts:profile")
    else:
        user_form = UserUpdateForm(
            instance=request.user
        )

        profile_form = ProfileUpdateForm(
            instance=profile
        )

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }

    return render(
        request,
        "accounts/profile_edit.html",
        context,
    )
def activation_sent(request):
    return render(
        request,
        "accounts/activation_sent.html",
    )


def activate_account(request, uidb64, token):
    try:
        user_id = urlsafe_base64_decode(
            uidb64
        ).decode()

        user = User.objects.get(pk=user_id)

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):
        user = None

    if (
        user is not None
        and default_token_generator.check_token(user, token)
    ):
        user.is_active = True
        user.save(update_fields=["is_active"])

        messages.success(
            request,
            "Your account was activated successfully. You can now login.",
        )

        return redirect("accounts:login")

    return render(
        request,
        "accounts/activation_invalid.html",
    )