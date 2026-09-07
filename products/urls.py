from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),

    path(
        "category/<slug:category_slug>/",
        views.product_list,
        name="category_products",
    ),

    path(
    "review/<int:product_id>/",
    views.add_review,
    name="add_review",
),

    path(
        "<slug:slug>/",
        views.product_detail,
        name="product_detail",
    ),
]
