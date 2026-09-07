from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from orders.models import Order
from products.models import Product


@staff_member_required
def dashboard_home(request):
    today = timezone.localdate()

    valid_orders = Order.objects.exclude(
        status="cancelled"
    )

    total_revenue = valid_orders.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    today_revenue = valid_orders.filter(
        created_at__date=today
    ).aggregate(
        total=Sum("total_price")
    )["total"] or 0

    order_statuses = Order.objects.values(
        "status"
    ).annotate(
        total=Count("id")
    ).order_by("status")

    recent_orders = Order.objects.select_related(
        "user"
    )[:10]

    low_stock_products = Product.objects.filter(
        stock__lte=5
    ).order_by("stock")[:10]

    context = {
        "total_revenue": total_revenue,
        "today_revenue": today_revenue,
        "total_orders": Order.objects.count(),
        "total_products": Product.objects.count(),
        "total_customers": User.objects.filter(
            is_staff=False
        ).count(),
        "pending_orders": Order.objects.filter(
            status="pending"
        ).count(),
        "order_statuses": order_statuses,
        "recent_orders": recent_orders,
        "low_stock_products": low_stock_products,
    }

    return render(
        request,
        "dashboard/dashboard_home.html",
        context,
    )