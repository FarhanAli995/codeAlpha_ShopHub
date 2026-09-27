from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from core.permissions import staff_required
from orders.models import Order
from products.models import Product


@staff_required
def dashboard_view(request):
	"""Landing page for authenticated staff and superusers."""
	orders = Order.objects.select_related('user').order_by('-created_at')

	# ── 7-day sales trend (revenue per day for charting) ──
	today = timezone.now().date()
	trend_start = today - timedelta(days=6)
	sales_rows = (
		Order.objects
		.filter(created_at__date__gte=trend_start)
		.exclude(status__in=['cancelled', 'refunded'])
		.values('created_at__date')
		.annotate(total=Sum('total_amount'))
	)
	sales_by_day = {row['created_at__date']: float(row['total'] or 0) for row in sales_rows}
	sales_trend = []
	for offset in range(7):
		day = trend_start + timedelta(days=offset)
		sales_trend.append({
			'label': day.strftime('%a'),
			'value': round(sales_by_day.get(day, 0.0), 2),
		})

	# ── Order status breakdown (doughnut) ──
	status_rows = orders.values('status').annotate(count=Count('id')).order_by('-count')
	status_labels = dict(Order.STATUS_CHOICES)
	order_status_breakdown = [
		{'label': status_labels.get(row['status'], row['status']), 'value': row['count']}
		for row in status_rows
	]

	return render(request, 'dashboard/index.html', {
		'product_count': Product.objects.count(),
		'order_count': orders.count(),
		'customer_count': get_user_model().objects.filter(is_staff=False, is_superuser=False).count(),
		'pending_order_count': orders.filter(status='pending').count(),
		'recent_orders': orders[:6],
		'total_sales': orders.filter(status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0,
		'sales_trend': sales_trend,
		'sales_trend_max': max([row['value'] for row in sales_trend] + [1]),
		'order_status_breakdown': order_status_breakdown,
	})
