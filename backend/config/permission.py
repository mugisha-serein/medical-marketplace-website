from rest_framework.pagination import CursorPagination as _CursorPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger(__name__)


# ── Pagination ────────────────────────────────────────────────────────────────
class CursorPagination(_CursorPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-created_at'


# ── Exception handler ─────────────────────────────────────────────────────────
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            'error': True,
            'status_code': response.status_code,
            'detail': response.data,
        }
        # Log 5xx errors
        if response.status_code >= 500:
            logger.error('Server error', exc_info=exc, extra={'context': str(context)})
        response.data = error_data

    return response


# ── Permissions ───────────────────────────────────────────────────────────────
class IsVendor(BasePermission):
    message = 'Vendor account required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_vendor)


class IsCustomer(BasePermission):
    message = 'Customer account required.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_vendor)


class IsVendorOrAdmin(BasePermission):
    message = 'Vendor or admin account required.'

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            (request.user.is_vendor or request.user.is_staff)
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner field must match request.user."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        owner = getattr(obj, 'user', None) or getattr(obj, 'customer', None)
        return owner == request.user


class VendorProductPermission(BasePermission):
    """Ensures vendor can only mutate their own products."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if not request.user.is_vendor:
            return False
        vendor_profile = getattr(request.user, 'vendor_profile', None)
        product_vendor = getattr(obj, 'vendor', None)
        return vendor_profile == product_vendor