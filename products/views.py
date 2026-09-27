from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, render
from decimal import Decimal, InvalidOperation

from .models import Brand, Category, Product


CATEGORY_GALLERY_FALLBACKS = {
	'home-products': [
		('https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=85', 'Home decor collection'),
		('https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=1200&q=85', 'Home interior collection'),
		('https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=1200&q=85', 'Modern home decor'),
	],
	'wearing-products': [
		('https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1200&q=85', 'Cotton clothing'),
		('https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=85', 'Contemporary fashion'),
		('https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=1200&q=85', 'Everyday fashion'),
	],
	'electronics': [
		('https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=1200&q=85', 'Consumer electronics'),
		('https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=85', 'Audio electronics'),
		('https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=1200&q=85', 'Personal electronics'),
	],
	'technology': [
		('https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=85', 'Technology components'),
		('https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=1200&q=85', 'Computer technology'),
		('https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1200&q=85', 'Technology workspace'),
	],
	'beauty-health': [
		('https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=1200&q=85', 'Beauty and skincare'),
		('https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=1200&q=85', 'Skincare products'),
		('https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=1200&q=85', 'Beauty products'),
	],
	'sports-outdoors': [
		('https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=85', 'Sports and fitness'),
		('https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=1200&q=85', 'Yoga and fitness'),
		('https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=1200&q=85', 'Outdoor hydration'),
	],
	'grocery-food': [
		('https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=1200&q=85', 'Fresh grocery produce'),
		('https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=85', 'Fresh meal ingredients'),
		('https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=85', 'Fresh garden salad'),
	],
	'books-stationery': [
		('https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=1200&q=85', 'Books and stationery'),
		('https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=1200&q=85', 'Books collection'),
		('https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=1200&q=85', 'Writing and stationery'),
	],
}

PRODUCT_GALLERY_FALLBACKS = {
	'home-table-lamp': [
		('https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1200&q=85', 'Modern table lamp on a side table'),
		('https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=1200&q=85', 'Table lamp in a contemporary room'),
		('https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=1200&q=85', 'Modern lamp detail'),
	],
}


def product_list_view(request):
	products = Product.objects.filter(status='active').select_related('category', 'brand').prefetch_related('images')
	query = request.GET.get('q', '').strip()
	category_slug = request.GET.get('category', '').strip()
	brand_slug = request.GET.get('brand', '').strip()
	min_price = request.GET.get('min_price', '').strip()
	max_price = request.GET.get('max_price', '').strip()
	sort = request.GET.get('sort', 'newest')

	if query:
		products = products.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(brand__name__icontains=query))
	if category_slug:
		products = products.filter(category__slug=category_slug)
	if brand_slug:
		products = products.filter(brand__slug=brand_slug)
	try:
		min_value = Decimal(min_price) if min_price else None
		if min_value is not None and (not min_value.is_finite() or min_value < 0):
			min_value = None
	except InvalidOperation:
		min_value = None
	try:
		max_value = Decimal(max_price) if max_price else None
		if max_value is not None and (not max_value.is_finite() or max_value < 0):
			max_value = None
	except InvalidOperation:
		max_value = None
	if min_value is not None:
		products = products.filter(price__gte=min_value)
	if max_value is not None:
		products = products.filter(price__lte=max_value)

	sort_options = {
		'newest': '-created_at',
		'price_low': 'price',
		'price_high': '-price',
		'name': 'name',
	}
	products = products.order_by(sort_options.get(sort, '-created_at'))
	page = Paginator(products, 12).get_page(request.GET.get('page'))

	return render(request, 'products/product_list.html', {
		'page_obj': page,
		'products': page.object_list,
		'categories': Category.objects.filter(is_active=True).exclude(slug='electronics-6e0f3324'),
		'brands': Brand.objects.filter(is_active=True),
		'query': query,
		'selected_category': category_slug,
		'selected_brand': brand_slug,
		'min_price': str(min_value) if min_value is not None else '',
		'max_price': str(max_value) if max_value is not None else '',
		'sort': sort,
	})


def product_detail_view(request, slug):
	product = get_object_or_404(
		Product.objects.select_related('category', 'brand').prefetch_related('images', 'variants', 'reviews__user'),
		slug=slug,
		status='active',
	)
	gallery_images = [
		{
			'url': image.image.url,
			'alt': image.alt_text or product.name,
		}
		for image in product.images.all()
	]
	if not gallery_images:
		fallback_images = PRODUCT_GALLERY_FALLBACKS.get(
			product.slug,
			CATEGORY_GALLERY_FALLBACKS.get(product.category.slug, []),
		)
		gallery_images = [
			{
				'url': url,
				'alt': alt,
			}
			for url, alt in fallback_images
		]
	related_products = Product.objects.filter(status='active', category=product.category).exclude(pk=product.pk)[:4]
	reviews = product.reviews.filter(status='approved').select_related('user')
	return render(request, 'products/product_detail.html', {
		'product': product,
		'gallery_images': gallery_images,
		'related_products': related_products,
		'reviews': reviews,
		'variants': product.variants.filter(is_active=True),
		'average_rating': reviews.aggregate(value=Avg('rating'))['value'] or 0,
	})
