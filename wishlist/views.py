from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .models import WishlistItem


@login_required
def wishlist_detail(request):
    wishlist_items = WishlistItem.objects.filter(
        user=request.user,
    ).select_related(
        "product",
        "product__category",
    )

    return render(
        request,
        "wishlist/wishlist_detail.html",
        {"wishlist_items": wishlist_items},
    )


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    wishlist_item = WishlistItem.objects.filter(
        user=request.user,
        product=product,
    ).first()

    if wishlist_item:
        wishlist_item.delete()

        messages.success(
            request,
            f"{product.name} was removed from your wishlist.",
        )
    else:
        WishlistItem.objects.create(
            user=request.user,
            product=product,
        )

        messages.success(
            request,
            f"{product.name} was added to your wishlist.",
        )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("wishlist:wishlist_detail")