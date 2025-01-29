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
        try:
            print(f"Before Token Validation - Request User: {request.user}")  # Debug log

            profile = validate_token(request)  # Validate the token and fetch the profile
            if not profile:
                print("Profile not found for the request.")
                return False
            

            role = profile.role
            print(f"Role in Permission Check: {role}")
            print(f"After Token Validation - Request User: {request.user}")  # Debug log

            print(f"Object User: {obj.user}, Request User: {request.user}")
            if role == 'admin':
                return True
            elif role == 'staff':
                return obj.staff == request.user
            elif role == 'client':
                return obj.user == request.user
            return False
        except Exception as e:
            print("Error in IsAdminOrOwner:", str(e))
            return False