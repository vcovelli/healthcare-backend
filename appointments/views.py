from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentSerializer, ProfileSerializer
from django.contrib.auth.models import User



# Custom permission to handle role-based access
class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admins to view and manage all appointments.
    - Staff to view and manage appointments related to them.
    - Clients to only view and manage their own appointments.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.profile.role == 'admin':
            return True  # Admins can access everything
        elif request.user.profile.role == 'staff':
            # Staff can access appointments associated with them
            return obj.staff == request.user
        elif request.user.profile.role == 'client':
            # Clients can only access their own appointments
            return obj.user == request.user
        return False

# View for listing and creating appointments
class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    API view to list all appointments or create a new appointment.
    - Admins can see all appointments.
    - Clients can only see their own appointments.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'admin':
            return Appointment.objects.all()  # Admins see all appointments
        elif user.profile.role == 'staff':
            return Appointment.objects.filter(staff=user)  # Staff see their assigned appointments
        elif user.profile.role == 'client':
            return Appointment.objects.filter(user=user)  # Clients see their own appointments
        return Appointment.objects.none()  # Default to no access if role is undefined
    
    def perform_create(self, serializer):
        """
        Automatically assign the logged-in user as the client
        when they create an appointment.
        """
        user = self.request.user
        if user.profile.role != 'client':
            raise PermissionDenied("Only clients can create appointments.")
        serializer.save(user=user)
    
# View for retrieving, updating, and deleting a specific appointment
class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific appointment.
    - Admins can manage all appointments.
    - Staff can manage appointments assigned to them.
    - Clients can only manage their own appointments.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'admin':
            return Appointment.objects.all()  # Admins see all appointments
        elif user.profile.role == 'staff':
            return Appointment.objects.filter(staff=user)  # Staff see their assigned appointments
        elif user.profile.role == 'client':
            return Appointment.objects.filter(user=user)  # Clients see their own appointments
        return Appointment.objects.none()  # Default to no access if role is undefined
    
# View for creating user profiles
class CreateProfileView(APIView):
    """
    API view to create user profiles.
    Only admins can create profiles for other users.
    """

    def post(self, request, *args, **kwargs):
        user = request.user

        # Check if the requesting user is an admin
        if not user.is_staff and user.profile.role != 'admin':
            return Response(
                {"detail": "Only admins can create profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Validate the request data and create the profile
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)