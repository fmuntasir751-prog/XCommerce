from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Category, Product, Review


def product_list(request, category_slug=None):
    products = Product.objects.filter(
    is_available=True
).select_related(
    "category"
).annotate(
    average_rating=Avg("reviews__rating")
)

    categories = Category.objects.filter(
        is_active=True
    )

    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(
            Category,
            slug=category_slug,
            is_active=True,
        )

        products = products.filter(
            category=selected_category
        )

    query = request.GET.get("q", "").strip()

    if query:
        products = products.filter(
            name__icontains=query
        )

    context = {
        "products": products,
        "categories": categories,
        "selected_category": selected_category,
        "query": query,
    }

    return render(
        request,
        "products/product_list.html",
        context,
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug,
        is_available=True,
    )

    reviews = product.reviews.select_related(
        "user"
    )

    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"] or 0

    user_review = None

    if request.user.is_authenticated:
        user_review = reviews.filter(
            user=request.user
        ).first()

    review_form = ReviewForm(
        instance=user_review
    )

    related_products = Product.objects.filter(
        category=product.category,
        is_available=True,
    ).exclude(
        pk=product.pk
    )[:4]

    context = {
        "product": product,
        "reviews": reviews,
        "review_count": reviews.count(),
        "average_rating": average_rating,
        "review_form": review_form,
        "user_review": user_review,
        "related_products": related_products,
    }

    return render(
        request,
        "products/product_detail.html",
        context,
    )


@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    existing_review = Review.objects.filter(
        product=product,
        user=request.user,
    ).first()

    form = ReviewForm(
        request.POST,
        instance=existing_review,
    )

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

        if existing_review:
            messages.success(
                request,
                "Your review was updated successfully.",
            )
        else:
            messages.success(
                request,
                "Thank you for reviewing this product.",
            )
    else:
        messages.error(
            request,
            "Please select a rating and write a comment.",
        )

    return redirect(product.get_absolute_url())