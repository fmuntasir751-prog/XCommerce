import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.utils import timezone

from cart.cart import Cart
from products.models import Product

from .forms import CheckoutForm
from .models import Order, OrderItem
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@login_required
def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)

    if not cart_items:
        messages.warning(
            request,
            "Your cart is empty.",
        )
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
                    order.total_price = (
                        cart.get_total_price()
                    )
                    order.payment_status = "unpaid"
                    order.save()

                    stripe_line_items = []

                    for item in cart_items:
                        product = (
                            Product.objects
                            .select_for_update()
                            .get(
                                pk=item["product"].pk
                            )
                        )

                        if product.stock < item["quantity"]:
                            raise ValueError(
                                f"Only {product.stock} "
                                f"item(s) of "
                                f"{product.name} "
                                f"are available."
                            )

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=item["price"],
                            quantity=item["quantity"],
                        )

                        stripe_line_items.append(
                            {
                                "price_data": {
                                    "currency": "jpy",
                                    "product_data": {
                                        "name": product.name,
                                    },
                                    "unit_amount": int(
                                        item["price"]
                                    ),
                                },
                                "quantity": item["quantity"],
                            }
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

                    checkout_url = None

                    if order.payment_method == "card":
                        stripe.api_key = (
                            settings.STRIPE_SECRET_KEY
                        )

                        success_path = reverse(
                            "orders:payment_success",
                            kwargs={
                                "order_id": order.id,
                            },
                        )

                        success_url = (
                            request.build_absolute_uri(
                                success_path
                            )
                            + "?session_id="
                            + "{CHECKOUT_SESSION_ID}"
                        )

                        cancel_path = reverse(
                            "orders:payment_cancel",
                            kwargs={
                                "order_id": order.id,
                            },
                        )

                        cancel_url = (
                            request.build_absolute_uri(
                                cancel_path
                            )
                        )

                        checkout_session = (
                            stripe.checkout.Session.create(
                                mode="payment",
                                payment_method_types=[
                                    "card"
                                ],
                                line_items=(
                                    stripe_line_items
                                ),
                                success_url=success_url,
                                cancel_url=cancel_url,
                                customer_email=order.email,
                                client_reference_id=str(
                                    order.id
                                ),
                                metadata={
                                    "order_id": str(
                                        order.id
                                    ),
                                    "user_id": str(
                                        request.user.id
                                    ),
                                },
                            )
                        )

                        order.stripe_session_id = (
                            checkout_session.id
                        )

                        order.save(
                            update_fields=[
                                "stripe_session_id",
                            ]
                        )

                        checkout_url = (
                            checkout_session.url
                        )

                    cart.clear()

                if checkout_url:
                    return redirect(checkout_url)

                messages.success(
                    request,
                    "Your order was placed successfully.",
                )

                return redirect(
                    "orders:order_success",
                    order_id=order.id,
                )

            except ValueError as error:
                messages.error(
                    request,
                    str(error),
                )

            except stripe.StripeError as error:
                error_message = (
                    getattr(
                        error,
                        "user_message",
                        None,
                    )
                    or str(error)
                )

                messages.error(
                    request,
                    f"Stripe error: {error_message}",
                )

            except Exception as error:
                messages.error(
                    request,
                    f"Payment setup error: {error}",
                )

    else:
        form = CheckoutForm(
            initial=initial_data
        )

    context = {
        "form": form,
        "cart": cart,
        "cart_items": cart_items,
    }

    return render(
        request,
        "orders/checkout.html",
        context,
    )


@login_required
def payment_success(request, order_id):
    session_id = request.GET.get("session_id")

    if not session_id:
        messages.error(
            request,
            "Payment session was not found.",
        )
        return redirect("orders:order_history")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        checkout_session = (
            stripe.checkout.Session.retrieve(
                session_id
            )
        )

    except stripe.StripeError as error:
        error_message = (
            getattr(
                error,
                "user_message",
                None,
            )
            or str(error)
        )

        messages.error(
            request,
            f"Unable to verify payment: "
            f"{error_message}",
        )

        return redirect("orders:order_history")

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        stripe_session_id=checkout_session.id,
    )

    # Stripe 15.x metadata is a StripeObject.
    metadata = (
        checkout_session.metadata.to_dict()
    )

    session_order_id = metadata.get(
        "order_id"
    )

    if (
        str(order.id) == session_order_id
        and checkout_session.payment_status
        == "paid"
    ):
        if order.payment_status != "paid":
            order.payment_status = "paid"
            order.status = "processing"

            if checkout_session.payment_intent:
                order.stripe_payment_intent_id = str(
                    checkout_session.payment_intent
                )

            order.paid_at = timezone.now()

            order.save(
                update_fields=[
                    "payment_status",
                    "status",
                    "stripe_payment_intent_id",
                    "paid_at",
                ]
            )

        messages.success(
            request,
            "Payment completed successfully.",
        )

        return redirect(
            "orders:order_success",
            order_id=order.id,
        )

    messages.error(
        request,
        "Payment has not been completed.",
    )

    return redirect("orders:order_history")


@login_required
def payment_cancel(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        payment_method="card",
    )

    messages.warning(
        request,
        f"Payment for Order #{order.id} "
        f"was cancelled. The order remains unpaid.",
    )

    return redirect(
        "orders:order_success",
        order_id=order.id,
    )


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
        {
            "order": order,
        },
    )


@login_required
def order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
    )

    return render(
        request,
        "orders/order_history.html",
        {
            "orders": orders,
        },
    )
@csrf_exempt
def stripe_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    payload = request.body
    signature = request.META.get(
        "HTTP_STRIPE_SIGNATURE"
    )

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:
        return HttpResponse(status=400)

    except stripe.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_data = session.to_dict()

        metadata = session_data.get(
            "metadata",
            {}
        )

        order_id = metadata.get("order_id")
        session_id = session_data.get("id")
        payment_status = session_data.get(
            "payment_status"
        )

        if (
            order_id
            and session_id
            and payment_status == "paid"
        ):
            order = Order.objects.filter(
                id=order_id,
                stripe_session_id=session_id,
                payment_method="card",
            ).first()

            if (
                order
                and order.payment_status != "paid"
            ):
                order.payment_status = "paid"
                order.status = "processing"
                order.stripe_payment_intent_id = (
                    session_data.get(
                        "payment_intent"
                    )
                )
                order.paid_at = timezone.now()

                order.save(
                    update_fields=[
                        "payment_status",
                        "status",
                        "stripe_payment_intent_id",
                        "paid_at",
                    ]
                )

    return HttpResponse(status=200)