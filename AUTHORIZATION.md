# ShopHub authorization

## Authentication versus authorization

Authentication answers **who is this user?** Django handles it with the custom `CustomUser` model, password hashing, sessions, `login_required`, and the login views.

Authorization answers **what may this authenticated user do?** ShopHub uses Django's `is_staff`, `is_superuser`, groups, and model permissions. A successful login does not grant access to staff tools.

## Access levels

- **Customer:** authenticated customer features such as cart, checkout, orders, reviews, profile, and addresses. Customers do not have `is_staff` and cannot access `/admin/` or `/dashboard/`.
- **Staff/Admin:** `is_staff=True` and one or more ShopHub groups. The groups control model-level access.
- **Superuser:** `is_superuser=True`. Django grants full model permissions and full Admin access.

## Groups

Run this after migrations:

```powershell
python manage.py migrate
python manage.py setup_authorization
```

The command is safe to run repeatedly. It creates or updates these groups:

- **Product Manager:** products, variants, images, inventory, brands, and categories.
- **Order Manager:** orders and order items.
- **Customer Manager:** users, profiles, and addresses.
- **Content Manager:** coupons, coupon usage, reviews, and notifications.

Each group receives Django's `add`, `change`, `delete`, and `view` permissions for its models. Assign only the permissions required by your deployment; the command resets each managed group's permission set to this baseline.

## Assigning access

Use Django Admin as a superuser:

1. Open `/admin/` and select **Users**.
2. Set `is_staff` only for trusted staff accounts.
3. Add one or more groups to the user.
4. For finer control, edit the group's permissions or assign individual user permissions.

A staff user without a group can authenticate to Django Admin but cannot manage ShopHub models. A superuser bypasses group restrictions. View code should use `@staff_required`, `@group_required(...)`, `@permission_required('app_label.change_model')`, `StaffRequiredMixin`, or `GroupRequiredMixin` at the view boundary.
