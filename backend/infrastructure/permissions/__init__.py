"""Base permission classes for DRF views."""
from rest_framework.permissions import BasePermission, IsAuthenticated
from infrastructure.exceptions import AuthorizationError


class IsOwner(BasePermission):
    """Allow access only if user is the object owner."""
    
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class IsVendor(IsAuthenticated):
    """Allow access only if user is a verified vendor."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_vendor and request.user.vendor_profile.is_verified


class IsAdmin(IsAuthenticated):
    """Allow access only if user is admin."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff


class IsAdminOrOwner(BasePermission):
    """Allow admin or owner."""
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_id == request.user.id


__all__ = ['IsOwner', 'IsVendor', 'IsAdmin', 'IsAdminOrOwner']
