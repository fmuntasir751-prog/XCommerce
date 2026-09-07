from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product

from .cart import Cart


def cart_detail(request):
    cart = Cart(request)

    return render(
        request,
        "cart/cart_detail.html",
        {"cart": cart},
    )


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(1, min(quantity, product.stock))

    cart.add(
        product=product,
        quantity=quantity,
        override_quantity=False,
    )

    messages.success(
        request,
        f"{product.name} was added to your cart.",
    )

    return redirect("cart:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        cart.remove(product)
    else:
        quantity = min(quantity, product.stock)

        cart.add(
            product=product,
            quantity=quantity,
            override_quantity=True,
        )

    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    cart.remove(product)

    messages.success(
        request,
        f"{product.name} was removed from your cart.",
    )

    return redirect("cart:cart_detail")
