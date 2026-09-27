from cart.models import Cart
from products.models import Category

def cart_item_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            cart = Cart.objects.filter(session_key=request.session.session_key, user__isnull=True).first()
        if cart:
            count = cart.total_items
    except Exception:
        pass
    categories = Category.objects.filter(is_active=True, parent__isnull=True)[:6]
    return {'cart_count': count, 'nav_categories': categories}
