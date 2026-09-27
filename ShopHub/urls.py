"""
Root URL configuration for ShopHub project.

Each app has its own urls.py and is included here with a URL prefix.
Media files are served by Django in development (DEBUG=True) only.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ── Django Admin ────────────────────────────────
    path('admin/', admin.site.urls),

    # ── Core (homepage, about, contact) ─────────────
    path('', include('core.urls')),

    # ── Accounts (register, login, logout, profile) ──
    path('accounts/', include('accounts.urls')),

    # ── Products (listings, detail, search, category) ─
    path('products/', include('products.urls')),

    # ── Cart (add, remove, update, view cart) ────────
    path('cart/', include('cart.urls')),

    # ── Orders (checkout, order history, detail) ─────
    path('orders/', include('orders.urls')),

    # ── Reviews (post, edit, delete review) ──────────
    path('reviews/', include('reviews.urls')),

    # ── Coupons (apply, validate coupon codes) ────────
    path('coupons/', include('coupons.urls')),

    # ── Dashboard (analytics, manage products/orders) ─
    path('dashboard/', include('dashboard.urls')),
]

# ── Serve media files in development ─────────────────
# In production, your web server (Nginx/Apache) handles /media/ URLs.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

