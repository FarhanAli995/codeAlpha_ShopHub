from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from products.models import Brand, Category, Product


# Simple icon mapping so category cards get a relevant Bootstrap Icon.
CATEGORY_ICONS = {
    'electronics': 'bi-cpu',
    'phones': 'bi-phone',
    'computers': 'bi-laptop',
    'fashion': 'bi-bag',
    'clothing': 'bi-bag',
    'shoes': 'bi-boots',
    'home': 'bi-house-heart',
    'kitchen': 'bi-cup-hot',
    'beauty': 'bi-stars',
    'health': 'bi-heart-pulse',
    'sports': 'bi-bicycle',
    'books': 'bi-book',
    'toys': 'bi-controller',
    'gaming': 'bi-controller',
    'groceries': 'bi-basket',
    'grocery': 'bi-basket',
    'accessories': 'bi-watch',
    'jewelry': 'bi-gem',
    'automotive': 'bi-car-front',
    'baby': 'bi-balloon',
    'pets': 'bi-heart',
    'office': 'bi-briefcase',
    'technology': 'bi-cpu-fill',
    'tech': 'bi-cpu-fill',
    'home products': 'bi-house-heart-fill',
    'homeproducts': 'bi-house-heart-fill',
    'wearing': 'bi-person-badge-fill',
    'wear': 'bi-person-badge-fill',
}

CATEGORY_OFFERS = {
    'home': ('Home refresh', 'Up to 35% off', 'quick-yellow'),
    'wear': ('Style season', 'Up to 45% off', 'quick-blue'),
    'fashion': ('Style season', 'Up to 45% off', 'quick-blue'),
    'electronics': ('Smart upgrades', 'Up to 25% off', 'quick-green'),
    'technology': ('Tech essentials', 'Up to 30% off', 'quick-green'),
    'grocery': ('Fresh market', 'Up to 20% off', 'quick-yellow'),
    'beauty': ('Beauty picks', 'Up to 40% off', 'quick-blue'),
    'sports': ('Move more', 'Up to 30% off', 'quick-green'),
}


def _category_icon(name):
    if not name:
        return 'bi-grid'
    key = name.strip().lower()
    if key in CATEGORY_ICONS:
        return CATEGORY_ICONS[key]
    for token, icon in CATEGORY_ICONS.items():
        if token in key:
            return icon
    return 'bi-grid'


def home_view(request):
    products = Product.objects.filter(status='active').select_related('category', 'brand').prefetch_related('images')
    featured = list(products.filter(is_featured=True)[:8])
    if not featured:
        # Nothing flagged as featured yet — surface newest products instead of an empty section.
        featured = list(products[:8])

    # Top-level categories with a real product count and a mapped icon.
    categories = list(
        Category.objects
        .filter(is_active=True, parent__isnull=True)
        .exclude(slug='electronics-6e0f3324')
        .annotate(product_count=Count('products', filter=Q(products__status='active')))
        .order_by('name')[:12]
    )
    for category in categories:
        category.icon = _category_icon(category.name)
        offer = next(
            (value for token, value in CATEGORY_OFFERS.items() if token in category.name.lower()),
            ('Category picks', 'Fresh deals inside', 'quick-yellow'),
        )
        category.offer_title, category.offer_text, category.offer_class = offer

    category_offers = categories[:6]

    # Deal of the day = the active product with the deepest discount.
    deal_product = max(
        (p for p in products[:60] if p.discount_percentage),
        key=lambda p: p.discount_percentage,
        default=None,
    )

    # Distinct brands that actually have active products.
    brands = (
        Brand.objects
        .filter(is_active=True, products__status='active')
        .distinct()
        .order_by('name')[:12]
    )

    fallback_products = [
        {'name': name, 'price': price}
        for name, price in [
            ('Fresh Green Lettuce', '2.99'), ('Fresh Organic Broccoli', '2.49'),
            ('Avocado Hass', '3.99'), ('Organic Milk', '4.99'),
            ('Watermelon', '5.99'), ('Fresh Coconut', '2.99'),
            ('Red Onion', '1.99'), ('Potato Chips', '3.49'),
            ('Cheddar Cheese', '6.99'), ('Fresh Coriander', '1.99'),
            ('Green Cabbage', '1.50'), ('Green Giant Peas', '3.99'),
            ('Mango Slices', '3.99'), ('Iceberg Lettuce', '2.99'),
            ('Premium Garden Salad', '5.99'),
        ]
    ]

    return render(request, 'core/home.html', {
        'categories': categories,
        'featured_products': featured,
        'new_products': products[:8],
        'product_total': products.count(),
        'category_total': Category.objects.filter(is_active=True).exclude(slug='electronics-6e0f3324').count(),
        'brands': brands,
        'deal_product': deal_product,
        'fallback_products': fallback_products,
        'category_offers': category_offers,
    })


def wishlist_view(request):
    product_slugs = request.session.get('wishlist', [])
    products = Product.objects.filter(slug__in=product_slugs, status='active').select_related('category').prefetch_related('images')
    return render(request, 'core/wishlist.html', {'products': products})


@require_POST
def wishlist_add_view(request, slug):
    product = get_object_or_404(Product, slug=slug, status='active')
    wishlist = request.session.get('wishlist', [])
    if slug not in wishlist:
        wishlist.append(slug)
        request.session['wishlist'] = wishlist
        messages.success(request, f'{product.name} added to your wishlist.')
    next_url = request.POST.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect('core:wishlist')


@require_POST
def wishlist_remove_view(request, slug):
    wishlist = request.session.get('wishlist', [])
    request.session['wishlist'] = [item for item in wishlist if item != slug]
    messages.info(request, 'Item removed from your wishlist.')
    return redirect('core:wishlist')

