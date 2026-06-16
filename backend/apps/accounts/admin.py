from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, VendorProfile, CustomerProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'is_vendor', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_vendor', 'is_staff', 'is_active', 'email_verified']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_vendor', 'email_verified', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'is_vendor')}),
    )


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'is_verified', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['company_name', 'user__email']
    actions = ['verify_vendors']

    def verify_vendors(self, request, queryset):
        queryset.update(is_verified=True)
    verify_vendors.short_description = 'Mark selected vendors as verified'


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'created_at']
    search_fields = ['user__email', 'organization']