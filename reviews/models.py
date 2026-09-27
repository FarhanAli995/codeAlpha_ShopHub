from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import CustomUser
from products.models import Product


# ─────────────────────────────────────────────────────────
# REVIEW
# ─────────────────────────────────────────────────────────
class Review(models.Model):
    """
    A star rating + written review for a product by a verified buyer.

    Key design decisions:
      • unique_together(user, product) — one review per user per product.
      • rating is 1–5 stars enforced by validators.
      • is_verified_purchase — True if the user actually ordered this product.
      • status field for admin moderation before reviews go live.

    Relationships:
      • ForeignKey → CustomUser  (CASCADE — deleting user removes reviews)
      • ForeignKey → Product     (CASCADE — deleting product removes reviews)
    """

    STATUS_CHOICES = [
        ('pending',  'Pending Moderation'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Minimum rating is 1 star.'),
            MaxValueValidator(5, message='Maximum rating is 5 stars.'),
        ],
        help_text='1 (worst) to 5 (best).',
    )
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)

    is_verified_purchase = models.BooleanField(
        default=False,
        help_text='Set to True if the user has a delivered order containing this product.',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    helpful_count = models.PositiveIntegerField(
        default=0,
        help_text='How many users marked this review as helpful.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        # Prevent a user from reviewing the same product twice
        unique_together = [('user', 'product')]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'status']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f'{self.rating}★ review by {self.user.email} on {self.product.name}'

