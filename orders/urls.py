from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    path(
        "success/<int:order_id>/",
        views.order_success,
        name="order_success",
    ),

    path(
        "history/",
        views.order_history,
        name="order_history",
    ),
    path(
    "payment/success/<int:order_id>/",
    views.payment_success,
    name="payment_success",
),

path(
    "payment/cancel/<int:order_id>/",
    views.payment_cancel,
    name="payment_cancel",
),
path(
    "stripe/webhook/",
    views.stripe_webhook,
    name="stripe_webhook",
),
]