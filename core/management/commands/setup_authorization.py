"""Create ShopHub staff groups and assign model permissions."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from accounts.models import Address, CustomUser, Profile
from coupons.models import Coupon, CouponUsage
from orders.models import Order, OrderItem
from products.models import Brand, Category, Inventory, Product, ProductImage, ProductVariant
from reviews.models import Review
from notifications.models import Notification


GROUP_PERMISSIONS = {
    'Product Manager': [
        Category, Brand, Product, ProductImage, ProductVariant, Inventory,
    ],
    'Order Manager': [Order, OrderItem],
    'Customer Manager': [CustomUser, Profile, Address],
    'Content Manager': [Coupon, CouponUsage, Review, Notification],
}

PERMISSION_ACTIONS = ('add', 'change', 'delete', 'view')


class Command(BaseCommand):
    help = 'Create ShopHub authorization groups and assign model permissions.'

    def handle(self, *args, **options):
        for group_name, models in GROUP_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            permissions = []
            for model in models:
                content_type = ContentType.objects.get_for_model(model)
                permissions.extend(
                    Permission.objects.filter(
                        content_type=content_type,
                        codename__in={
                            f'{action}_{model._meta.model_name}'
                            for action in PERMISSION_ACTIONS
                        },
                    )
                )
            group.permissions.set(permissions)
            self.stdout.write(
                self.style.SUCCESS(
                    f'{group_name}: {len(permissions)} permissions assigned'
                )
            )

        self.stdout.write(
            'Superusers retain full access. Set is_staff=True only for trusted '
            'users who need Django Admin access.'
        )
