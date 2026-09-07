from django.db.models import Avg
from django.shortcuts import render

from orders.models import OrderItem
from products.models import Category, Product
from wishlist.models import WishlistItem


def home(request):
    categories = Category.objects.filter(
        is_active=True
    )[:6]

    available_products = Product.objects.filter(
        is_available=True
    ).select_related(
        "category"
    ).annotate(
        average_rating=Avg("reviews__rating")
    )

    personalized = False

    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(
            user=request.user
        )

        ordered_items = OrderItem.objects.filter(
            order__user=request.user
        )

        category_ids = set(
            wishlist_items.values_list(
                "product__category_id",
                flat=True,
            )
        )

        category_ids.update(
            ordered_items.values_list(
                "product__category_id",
                flat=True,
            )
        )

        excluded_product_ids = set(
            wishlist_items.values_list(
                "product_id",
                flat=True,
            )
        )

        excluded_product_ids.update(
            ordered_items.values_list(
                "product_id",
                flat=True,
            )
        )

        if category_ids:
            recommended_products = available_products.filter(
                category_id__in=category_ids
            ).exclude(
                id__in=excluded_product_ids
            ).distinct()[:8]

            if recommended_products:
                featured_products = recommended_products
                personalized = True
            else:
                featured_products = available_products.filter(
                    is_featured=True
                )[:8]
        else:
            featured_products = available_products.filter(
                is_featured=True
            )[:8]
    else:
        featured_products = available_products.filter(
            is_featured=True
        )[:8]

    context = {
        "categories": categories,
        "featured_products": featured_products,
        "personalized": personalized,
    }

    return render(
        request,
        "core/home.html",
        context,
    )