from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import CustomUser
from products.models import Product, ProductVariant


# ─────────────────────────────────────────────────────────
# CART
# ─────────────────────────────────────────────────────────
class Cart(models.Model):
    """
    One cart per user session.
    Supports both authenticated users and guests (session_key).

    Relationships:
      • ForeignKey → CustomUser (NULL for guest carts)
        Deleting the user deletes their cart (CASCADE).
      • One Cart ──► Many CartItem
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        help_text='NULL means this is a guest/anonymous cart.',
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        help_text='Django session key for guest carts.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        owner = self.user.email if self.user else f'Guest ({self.session_key})'
        return f'Cart of {owner}'

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())


# ─────────────────────────────────────────────────────────
# CART ITEM
# ─────────────────────────────────────────────────────────
class CartItem(models.Model):
    """
    One row in the cart for a specific product (and optional variant).

    Relationships:
      • ForeignKey → Cart    (many items belong to one cart; CASCADE delete)
      • ForeignKey → Product (what product is in the cart; SET_NULL on delete
                              so cart stays even if product is removed)
      • ForeignKey → ProductVariant (optional; NULL for non-variant products)
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items',
        help_text='The specific variant chosen (color, size, etc.)',
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    # Snapshot the price at the moment of adding to cart
    # so price changes don't silently affect existing carts
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        # A cart cannot have the same product+variant combo twice
        unique_together = [('cart', 'product', 'variant')]

    def __str__(self):
        variant_label = f' ({self.variant.name})' if self.variant else ''
        return f'{self.quantity}x {self.product.name}{variant_label}'

    @property
    def line_total(self):
        return self.unit_price * self.quantity

