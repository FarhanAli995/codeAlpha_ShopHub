"""Reusable authorization helpers for ShopHub views."""

from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required as django_permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView


GROUP_PRODUCT_MANAGER = 'Product Manager'
GROUP_ORDER_MANAGER = 'Order Manager'
GROUP_CUSTOMER_MANAGER = 'Customer Manager'
GROUP_CONTENT_MANAGER = 'Content Manager'
STAFF_GROUPS = {
    GROUP_PRODUCT_MANAGER,
    GROUP_ORDER_MANAGER,
    GROUP_CUSTOMER_MANAGER,
    GROUP_CONTENT_MANAGER,
}


def is_staff_or_superuser(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)


def staff_required(view_func):
    """Require an authenticated staff member for an internal view."""
    return user_passes_test(is_staff_or_superuser, login_url='accounts:login')(view_func)


def group_required(*group_names):
    """Require membership in one of the supplied groups or superuser status."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user = request.user
            if not user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path(), 'accounts:login')
            if user.is_superuser or user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapped
    return decorator


def permission_required(permission, **kwargs):
    """Require a Django model permission, with superuser support."""
    return django_permission_required(permission, raise_exception=True, **kwargs)


class StaffRequiredMixin:
    """Class-based-view equivalent of :func:`staff_required`."""

    def dispatch(self, request, *args, **kwargs):
        if not is_staff_or_superuser(request.user):
            from django.contrib.auth.views import redirect_to_login
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), 'accounts:login')
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class GroupRequiredMixin:
    """Class-based-view mixin for group or superuser access."""

    required_groups = ()

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), 'accounts:login')
        if not user.is_superuser and not user.groups.filter(name__in=self.required_groups).exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
