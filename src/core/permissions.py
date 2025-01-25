from rest_framework.permissions import BasePermission
from rest_framework import permissions
from src.core.utils import validate_token

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == 'admin'

class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == 'staff'

class IsClientUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == 'client'

# Custom permission to handle role-based access
class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admins to view and manage all appointments.
    - Staff to view and manage appointments related to them.
    - Clients to only view and manage their own appointments.
    """

    def has_object_permission(self, request, view, obj):
        role = validate_token(request).get("role", "client")
        print("Role in Permission Check:", role)  # Debugging role
        print("Object User:", obj.user, "Request User:", request.user)  # Debugging object ownership

        if role == 'admin':
            return True  # Admins can access everything
        elif role == 'staff':
            return obj.staff == request.user # Staff can access appointments associated with them
        elif role == 'client': 
            return obj.user == request.user # Clients can only access their own appointments
        return False