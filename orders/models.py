from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import CustomUser, Address
from products.models import Product, ProductVariant
from coupons.models import Coupon


# ─────────────────────────────────────────────────────────
# ORDER
# ─────────────────────────────────────────────────────────
class Order(models.Model):
    """
    Represents a customer's placed order.

    Relationships:
      • ForeignKey → CustomUser  (one user can have many orders; CASCADE)
      • ForeignKey → Address     (shipping address; SET_NULL so order survives
                                  even if the address is deleted)
      • ForeignKey → Coupon      (optional discount applied; SET_NULL)
      • One Order ──► Many OrderItem
    """

    STATUS_CHOICES = [
        ('pending',    'Pending'),       # just placed, awaiting payment
        ('confirmed',  'Confirmed'),     # payment received
        ('processing', 'Processing'),    # being packed
        ('shipped',    'Shipped'),       # handed to courier
        ('delivered',  'Delivered'),     # customer received it
        ('cancelled',  'Cancelled'),
        ('refunded',   'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod',    'Cash on Delivery'),
        ('card',   'Credit / Debit Card'),
        ('easypaisa', 'EasyPaisa'),
        ('jazzcash',  'JazzCash'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid',   'Unpaid'),
        ('paid',     'Paid'),
        ('refunded', 'Refunded'),
        ('failed',   'Failed'),
    ]

    # Unique human-readable order reference e.g. ORD-20241025-0001
    order_number = models.CharField(max_length=50, unique=True, editable=False)

    # Relationships
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )

    # Money — all DecimalField
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    shipping_cost = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    tax_amount = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='subtotal − discount + shipping + tax',
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod',
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='unpaid',
    )

    # Shipping info snapshot (in case address is later edited)
    shipping_name = models.CharField(max_length=150, blank=True)
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_street = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True, null=True, help_text='Customer notes / special instructions.')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order_number']),
        ]

    def __str__(self):
        return f'Order {self.order_number} by {self.user.email}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f'ORD-{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────
# ORDER ITEM
# ─────────────────────────────────────────────────────────
class OrderItem(models.Model):
    """
    A single line in an order.

    IMPORTANT: product_name, product_sku, and unit_price are SNAPSHOTS
    taken at the time of purchase. This preserves purchase history even
    if the product is renamed, repriced, or deleted later.

    Relationships:
      • ForeignKey → Order    (many items in one order; CASCADE)
      • ForeignKey → Product  (SET_NULL — order item survives product deletion)
      • ForeignKey → ProductVariant (SET_NULL — optional)
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items',
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )

    # ── Historical snapshots (never change after order is placed) ──
    product_name = models.CharField(max_length=300)   # product name at purchase time
    product_sku  = models.CharField(max_length=100)   # SKU at purchase time
    variant_name = models.CharField(max_length=100, blank=True)

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Price per unit at the moment the order was placed.',
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='unit_price × quantity, stored for reporting accuracy.',
    )

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.quantity}x {self.product_name} (Order {self.order.order_number})'

    def save(self, *args, **kwargs):
        # Auto-calculate line_total before saving
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

