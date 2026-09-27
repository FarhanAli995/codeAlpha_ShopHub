from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Address


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ('email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active')
    list_filter   = ('role', 'is_active', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)
    fieldsets     = UserAdmin.fieldsets + (
        ('ShopHub Extra', {'fields': ('phone', 'role', 'is_verified', 'date_of_birth')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'website', 'created_at')
    search_fields = ('user__email',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'user', 'city', 'country', 'is_primary')
    list_filter   = ('country', 'is_primary')
    search_fields = ('full_name', 'user__email', 'city')

