from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# ─────────────────────────────────────────────────────────
# CUSTOM USER
# ─────────────────────────────────────────────────────────
class CustomUser(AbstractUser):
    """
    Extends Django's built-in User.
    Adds phone number and an 'is_seller' flag so a user can manage products.

    Relationship summary:
      • One CustomUser ──► One Profile      (via OneToOneField in Profile)
      • One CustomUser ──► Many Address     (via ForeignKey in Address)
      • One CustomUser ──► Many Order       (via ForeignKey in Order)
      • One CustomUser ──► Many Review      (via ForeignKey in Review)
      • One CustomUser ──► Many Notification
    """

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('seller',   'Seller'),
        ('admin',    'Admin'),
    ]

    email = models.EmailField(
        _('email address'),
        unique=True,   # email must be unique across all users
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Include country code, e.g. +92-300-1234567',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='True once the user confirms their email address.',
    )
    date_of_birth = models.DateField(blank=True, null=True)

    # Use email as the login field instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'

    @property
    def is_seller(self):
        return self.role == 'seller'


# ─────────────────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────────────────
class Profile(models.Model):
    """
    Extended information for a user.

    Relationship:
      • OneToOne with CustomUser → every user has exactly one profile.
        Deleting the user also deletes the profile (CASCADE).
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',   # access as: user.profile
    )
    avatar = models.ImageField(
        upload_to='avatars/',     # saved under MEDIA_ROOT/avatars/
        blank=True,
        null=True,
        default='avatars/default.png',
    )
    bio = models.TextField(blank=True, null=True, max_length=500)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'Profile of {self.user.email}'


# ─────────────────────────────────────────────────────────
# ADDRESS
# ─────────────────────────────────────────────────────────
class Address(models.Model):
    """
    A user can have multiple saved addresses (home, work, etc.).
    Only one address per user can be marked as primary.

    Relationship:
      • ForeignKey to CustomUser → many addresses belong to one user.
        Deleting the user deletes all their addresses (CASCADE).
    """

    ADDRESS_TYPE_CHOICES = [
        ('home',   'Home'),
        ('work',   'Work'),
        ('other',  'Other'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='addresses',   # access as: user.addresses.all()
    )
    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES,
        default='home',
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Pakistan')
    postal_code = models.CharField(max_length=20)
    is_primary = models.BooleanField(
        default=False,
        help_text='Checked = this address is pre-selected at checkout.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        indexes = [
            models.Index(fields=['user', 'is_primary']),
        ]

    def __str__(self):
        return f'{self.full_name} – {self.city}, {self.country}'

    def save(self, *args, **kwargs):
        # If this address is marked primary, unmark all others for this user
        if self.is_primary:
            Address.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

