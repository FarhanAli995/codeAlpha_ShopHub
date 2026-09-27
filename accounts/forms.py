from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.core.exceptions import ValidationError
from .models import CustomUser, Profile, Address


# ─────────────────────────────────────────────────────────
# REGISTRATION FORM
# ─────────────────────────────────────────────────────────
class RegistrationForm(forms.ModelForm):
    """
    Collects first_name, last_name, email, password, password2.
    Email is used as USERNAME_FIELD so we validate uniqueness here.
    """

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'id': 'id_password',
        }),
        min_length=8,
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repeat your password',
            'id': 'id_password2',
        }),
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'First name', 'id': 'id_first_name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Last name', 'id': 'id_last_name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'you@example.com', 'id': 'id_email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '+92-300-1234567', 'id': 'id_phone',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generate a username from the email (required by AbstractUser)
        base = self.cleaned_data['email'].split('@')[0]
        username = base
        n = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f'{base}{n}'
            n += 1
        user.username = username
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Auto-create Profile for every new user
            Profile.objects.get_or_create(user=user)
        return user


# ─────────────────────────────────────────────────────────
# LOGIN FORM  (thin wrapper — just adds Bootstrap classes)
# ─────────────────────────────────────────────────────────
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'autofocus': True,
            'id': 'id_login_email',
        }),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your password',
            'id': 'id_login_password',
        }),
    )


# ─────────────────────────────────────────────────────────
# PROFILE UPDATE FORM
# ─────────────────────────────────────────────────────────
class ProfileUpdateForm(forms.ModelForm):
    """Updates the basic user info (name, phone)."""

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_pf_first_name'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'id': 'id_pf_last_name'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'id': 'id_pf_phone'}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date', 'id': 'id_pf_dob',
            }),
        }


class ProfileAvatarForm(forms.ModelForm):
    """Updates just the avatar and bio."""

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'website']
        widgets = {
            'bio':     forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'id_pf_bio'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'id': 'id_pf_website'}),
            'avatar':  forms.FileInput(attrs={'class': 'form-control', 'id': 'id_pf_avatar'}),
        }


# ─────────────────────────────────────────────────────────
# ADDRESS FORM
# ─────────────────────────────────────────────────────────
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user', 'created_at']
        widgets = {
            'address_type':   forms.Select(attrs={'class': 'form-select', 'id': 'id_addr_type'}),
            'full_name':      forms.TextInput(attrs={'class': 'form-control', 'id': 'id_addr_name'}),
            'phone':          forms.TextInput(attrs={'class': 'form-control', 'id': 'id_addr_phone'}),
            'street_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'id': 'id_addr_street'}),
            'city':           forms.TextInput(attrs={'class': 'form-control', 'id': 'id_addr_city'}),
            'state':          forms.TextInput(attrs={'class': 'form-control', 'id': 'id_addr_state'}),
            'country':        forms.TextInput(attrs={'class': 'form-control', 'id': 'id_addr_country'}),
            'postal_code':    forms.TextInput(attrs={'class': 'form-control', 'id': 'id_addr_postal'}),
            'is_primary':     forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_addr_primary'}),
        }


# ─────────────────────────────────────────────────────────
# PASSWORD FORMS  (Bootstrap-styled wrappers)
# ─────────────────────────────────────────────────────────
class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
            'id': 'id_reset_email',
        })


class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
