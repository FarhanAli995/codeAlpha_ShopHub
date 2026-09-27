from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Address
from cart.models import Cart
from .models import Order, OrderItem


@login_required
def checkout_view(request):
	cart = Cart.objects.filter(user=request.user).first()
	if not cart or not cart.items.exists():
		messages.info(request, 'Your cart is empty. Add a product before checking out.')
		return redirect('cart:view')

	addresses = request.user.addresses.all().order_by('-is_primary', '-created_at')
	if request.method == 'POST':
		address = get_object_or_404(Address, pk=request.POST.get('address'), user=request.user)
		payment_method = request.POST.get('payment_method', 'cod')
		allowed_methods = {'cod'}
		if payment_method not in allowed_methods:
			messages.error(request, 'Choose a valid payment method.')
			return redirect('orders:checkout')

		with transaction.atomic():
			subtotal = cart.subtotal
			order = Order.objects.create(
				user=request.user,
				shipping_address=address,
				subtotal=subtotal,
				total_amount=subtotal,
				payment_method=payment_method,
				shipping_name=address.full_name,
				shipping_phone=address.phone,
				shipping_street=address.street_address,
				shipping_city=address.city,
				shipping_country=address.country,
			)
			for item in cart.items.select_related('product', 'variant'):
				OrderItem.objects.create(
					order=order,
					product=item.product,
					variant=item.variant,
					product_name=item.product.name,
					product_sku=item.product.sku,
					variant_name=item.variant.name if item.variant else '',
					unit_price=item.unit_price,
					quantity=item.quantity,
				)
			cart.delete()

		messages.success(request, 'Your order has been placed successfully.')
		return redirect('orders:detail', order_number=order.order_number)

	return render(request, 'orders/checkout.html', {
		'cart': cart,
		'items': cart.items.select_related('product', 'variant'),
		'addresses': addresses,
		'payment_methods': [('cod', 'Cash on Delivery')],
	})


@login_required
def order_list_view(request):
	orders = request.user.orders.prefetch_related('items').all()
	return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
	order = get_object_or_404(
		Order.objects.prefetch_related('items'),
		order_number=order_number,
		user=request.user,
	)
	return render(request, 'orders/order_detail.html', {'order': order})
