from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import Cart
from products.models import Product

from .forms import CheckoutForm
from .models import Order, OrderItem


@login_required
def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect("products:product_list")

    initial_data = {
        "full_name": request.user.get_full_name(),
        "email": request.user.email,
    }

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_price = cart.get_total_price()
                    order.save()

                    for item in cart_items:
                        product = Product.objects.select_for_update().get(
                            pk=item["product"].pk
                        )

                        if product.stock < item["quantity"]:
                            raise ValueError(
                                f"Only {product.stock} item(s) of "
                                f"{product.name} are available."
                            )

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=item["price"],
                            quantity=item["quantity"],
                        )

                        product.stock -= item["quantity"]

                        if product.stock == 0:
                            product.is_available = False

                        product.save(
                            update_fields=[
                                "stock",
                                "is_available",
                            ]
                        )

                    cart.clear()

                return redirect(
                    "orders:order_success",
                    order_id=order.id,
                )

            except ValueError as error:
                messages.error(request, str(error))
    else:
        form = CheckoutForm(initial=initial_data)

    context = {
        "form": form,
        "cart": cart,
        "cart_items": cart_items,
    }

    return render(request, "orders/checkout.html", context)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "orders/order_success.html",
        {"order": order},
    )


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user,
    ).prefetch_related("items")

    return render(
        request,
        "orders/order_history.html",
        {"orders": orders},
    )