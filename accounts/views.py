from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import (
    authenticate, login, logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy

from .forms import (
    RegistrationForm,
    LoginForm,
    ProfileUpdateForm,
    ProfileAvatarForm,
    AddressForm,
    StyledPasswordChangeForm,
    StyledPasswordResetForm,
    StyledSetPasswordForm,
)
from .models import CustomUser, Profile, Address


# ─────────────────────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────────────────────
def register_view(request):
    """
    How it works:
      1. Show blank RegistrationForm on GET.
      2. On POST, validate — if valid, create user + profile, log them in,
         redirect to home with success message.
      3. If errors, re-render with error messages (Bootstrap alert styling).

    Already logged-in users are redirected to home.
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    form = RegistrationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(
                request,
                f'Welcome to ShopHub, {user.first_name}! Your account has been created.'
            )
            return redirect('core:home')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'accounts/register.html', {'form': form})


# ─────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────
def login_view(request):
    """
    How it works:
      • Uses Django's AuthenticationForm which calls authenticate() internally.
      • We pass request to the form so Django can bind the session correctly.
      • After login, redirect to `next` param (e.g. the protected page the
        user tried to access) or fall back to home.
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'core:home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


# ─────────────────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────────────────
@login_required
def logout_view(request):
    """POST-only logout to prevent CSRF logout via GET."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


# ─────────────────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    """
    Shows two forms on one page:
      • ProfileUpdateForm  — updates CustomUser fields (name, phone, DOB)
      • ProfileAvatarForm  — updates Profile fields (avatar, bio, website)
    Both are handled via separate POST buttons distinguished by a hidden field.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    user_form    = ProfileUpdateForm(instance=request.user)
    avatar_form  = ProfileAvatarForm(instance=profile)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = ProfileUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Please fix the errors below.')

        elif 'update_avatar' in request.POST:
            avatar_form = ProfileAvatarForm(request.POST, request.FILES, instance=profile)
            if avatar_form.is_valid():
                avatar_form.save()
                messages.success(request, 'Avatar updated successfully.')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Could not update avatar.')

    return render(request, 'accounts/profile.html', {
        'user_form':   user_form,
        'avatar_form': avatar_form,
        'profile':     profile,
    })


# ─────────────────────────────────────────────────────────
# ADDRESS MANAGEMENT
# ─────────────────────────────────────────────────────────
@login_required
def address_list_view(request):
    """Lists all addresses belonging to the logged-in user."""
    addresses = request.user.addresses.all().order_by('-is_primary', '-created_at')
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_add_view(request):
    """Adds a new address for the logged-in user."""
    form = AddressForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, 'Address added successfully.')
        return redirect('accounts:address_list')
    return render(request, 'accounts/address_form.html', {
        'form': form, 'action': 'Add',
    })


@login_required
def address_edit_view(request, pk):
    """Edits an existing address — only the owner can edit it."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    form = AddressForm(request.POST or None, instance=address)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Address updated successfully.')
        return redirect('accounts:address_list')
    return render(request, 'accounts/address_form.html', {
        'form': form, 'action': 'Edit', 'address': address,
    })


@login_required
def address_delete_view(request, pk):
    """Deletes an address via POST — GET shows confirmation page."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted.')
        return redirect('accounts:address_list')
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


@login_required
def address_set_primary_view(request, pk):
    """Sets an address as primary (via POST)."""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        # The Address.save() method handles unsetting other primaries
        address.is_primary = True
        address.save()
        messages.success(request, f'"{address.full_name} – {address.city}" set as primary address.')
    return redirect('accounts:address_list')


# ─────────────────────────────────────────────────────────
# PASSWORD CHANGE  (logged-in user changes their own password)
# ─────────────────────────────────────────────────────────
@login_required
def password_change_view(request):
    """
    Uses Django's PasswordChangeForm which verifies the old password
    before allowing a new one. update_session_auth_hash() keeps the
    user logged in after the password changes.
    """
    form = StyledPasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)   # stay logged in
        messages.success(request, 'Password changed successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/password_change.html', {'form': form})


# ─────────────────────────────────────────────────────────
# PASSWORD RESET  (forgot password — sends email with token link)
# ─────────────────────────────────────────────────────────
class CustomPasswordResetView(PasswordResetView):
    """
    Step 1 — User enters email; Django sends a one-time reset link.
    Uses console email backend in development (printed to terminal).
    """
    template_name      = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    form_class         = StyledPasswordResetForm
    success_url        = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Step 2 — Tell the user to check their email."""
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Step 3 — User clicks the link; enters new password."""
    template_name = 'accounts/password_reset_confirm.html'
    form_class    = StyledSetPasswordForm
    success_url   = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Step 4 — Reset done; show success + link to login."""
    template_name = 'accounts/password_reset_complete.html'

