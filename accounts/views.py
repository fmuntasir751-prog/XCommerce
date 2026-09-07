from django.contrib import messages
from django.contrib.auth import login
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


def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)

            messages.success(
                request,
                "Your account was created successfully.",
            )

            return redirect("core:home")
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