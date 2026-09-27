from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


# ─────────────────────────────────────────────────────────
# COUPON
# ─────────────────────────────────────────────────────────
class Coupon(models.Model):
    """
    A discount coupon code that customers enter at checkout.

    Relationships:
      • One Coupon ──► Many CouponUsage (tracks who used it and when)
      • One Coupon ──► Many Order       (orders that used this coupon)
    """

    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage (%)'),
        ('fixed',      'Fixed Amount (PKR)'),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text='The code customers enter, e.g. SUMMER20',
    )
    description = models.CharField(max_length=250, blank=True)
    discount_type = models.CharField(
        max_length=15,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
    )
    discount_value = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Percentage (0-100) or fixed PKR amount.',
    )
    # Caps maximum discount for percentage coupons (e.g. max PKR 500 off)
    max_discount_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    # Minimum cart total to be eligible
    minimum_order_value = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    # Usage limits
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Total number of times this coupon can be used. NULL = unlimited.',
    )
    usage_limit_per_user = models.PositiveIntegerField(
        default=1,
        help_text='How many times a single user can use this coupon.',
    )
    times_used = models.PositiveIntegerField(
        default=0,
        help_text='Auto-incremented. Do not edit manually.',
    )
    # Validity window
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'valid_from', 'valid_to']),
        ]

    def __str__(self):
        return f'{self.code} ({self.get_discount_type_display()} – {self.discount_value})'

    def is_valid(self):
        """Returns True if the coupon is currently active and within date range."""
        now = timezone.now()
        return (
            self.is_active
            and self.valid_from <= now <= self.valid_to
            and (self.usage_limit is None or self.times_used < self.usage_limit)
        )

    def calculate_discount(self, cart_total):
        """Returns the discount amount for a given cart total."""
        if not self.is_valid() or cart_total < self.minimum_order_value:
            return 0
        if self.discount_type == 'percentage':
            discount = (cart_total * self.discount_value) / 100
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = min(self.discount_value, cart_total)
        return round(discount, 2)


# ─────────────────────────────────────────────────────────
# COUPON USAGE
# ─────────────────────────────────────────────────────────
class CouponUsage(models.Model):
    """
    Tracks which user used which coupon on which order.
    Enforces per-user usage limits.

    Relationships:
      • ForeignKey → Coupon      (CASCADE — delete coupon = delete usage records)
      • ForeignKey → CustomUser  (CASCADE — delete user = delete usage records)
    The unique_together constraint prevents double-usage.
    """

    from accounts.models import CustomUser

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages',
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='coupon_usages',
    )
    # Store order_number as a plain string to avoid circular import with orders
    order_number = models.CharField(max_length=50, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        # A user cannot use the same coupon twice (per limit)
        unique_together = [('coupon', 'user', 'order_number')]

    def __str__(self):
        return f'{self.user.email} used {self.coupon.code} (Order {self.order_number})'

