from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from products.models import Product, ProductVariant
from .models import Cart, CartItem


def _get_cart(request):
	if request.user.is_authenticated:
		cart = Cart.objects.filter(user=request.user).first()
		return cart or Cart.objects.create(user=request.user)
	if not request.session.session_key:
		request.session.create()
	cart = Cart.objects.filter(session_key=request.session.session_key, user__isnull=True).first()
	return cart or Cart.objects.create(session_key=request.session.session_key)


def cart_view(request):
	cart = _get_cart(request)
	return render(request, 'cart/cart.html', {'cart': cart, 'items': cart.items.select_related('product', 'variant')})


@require_POST
def cart_add_view(request, slug):
	product = get_object_or_404(Product, slug=slug, status='active')
	cart = _get_cart(request)
	try:
		quantity = int(request.POST.get('quantity', 1))
	except (TypeError, ValueError):
		quantity = 1
	quantity = max(1, min(quantity, 99))
	variant_id = request.POST.get('variant_id')
	variant = None
	if variant_id:
		variant = get_object_or_404(ProductVariant, pk=variant_id, product=product, is_active=True)
		if variant.stock < 1:
			messages.error(request, 'That option is currently out of stock.')
			return redirect('products:detail', slug=slug)
	item_query = CartItem.objects.filter(cart=cart, product=product, variant=variant)
	item = item_query.first()
	if item:
		item.quantity = min(item.quantity + quantity, 99)
		item.save(update_fields=['quantity'])
	else:
		unit_price = variant.final_price if variant else product.price
		CartItem.objects.create(cart=cart, product=product, variant=variant, unit_price=unit_price, quantity=quantity)
	messages.success(request, f'{product.name} added to your cart.')
	next_url = request.POST.get('next', '')
	if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
		return redirect(next_url)
	return redirect('cart:view')


@require_POST
def cart_update_view(request, item_id):
	item = get_object_or_404(CartItem, pk=item_id, cart=_get_cart(request))
	try:
		quantity = int(request.POST.get('quantity', 1))
	except (TypeError, ValueError):
		quantity = item.quantity
	if quantity < 1:
		item.delete()
	else:
		item.quantity = min(quantity, 99)
		item.save(update_fields=['quantity'])
	return redirect('cart:view')


@require_POST
def cart_remove_view(request, item_id):
	get_object_or_404(CartItem, pk=item_id, cart=_get_cart(request)).delete()
	messages.info(request, 'Item removed from your cart.')
	return redirect('cart:view')
