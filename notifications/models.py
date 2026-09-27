from django.db import models
from accounts.models import CustomUser


# ─────────────────────────────────────────────────────────
# NOTIFICATION
# ─────────────────────────────────────────────────────────
class Notification(models.Model):
    """
    In-app notifications for users (order updates, review approved, etc.).

    Relationships:
      • ForeignKey → CustomUser (CASCADE — deleting user removes notifications)
    """

    TYPE_CHOICES = [
        ('order_placed',    'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_shipped',   'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('review_approved', 'Review Approved'),
        ('review_rejected', 'Review Rejected'),
        ('coupon_received', 'Coupon Received'),
        ('low_stock',       'Low Stock Alert'),
        ('general',         'General'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default='general',
        db_index=True,
    )
    title = models.CharField(max_length=200)
    message = models.TextField()

    # Optional deep-link — e.g. '/orders/ORD-XXXX/' so clicking goes to the order
    link = models.CharField(max_length=300, blank=True, null=True)

    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        status = 'READ' if self.is_read else 'UNREAD'
        return f'[{status}] {self.title} → {self.user.email}'

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])

