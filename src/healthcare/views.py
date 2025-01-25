from rest_framework import generics, permissions, status, serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Appointment, Profile
from .serializers import AppointmentSerializer, ProfileSerializer
from django.contrib.auth.models import User
from firebase_admin import auth as firebase_auth, credentials, initialize_app, get_app
from firebase_admin.auth import get_user, verify_id_token
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from src.core.utils import validate_token
from src.core.permissions import IsAdminOrOwner


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
        profile = validate_token(self.request)  # Returns a Profile object
        if not profile:
            raise PermissionDenied("User profile not found.")
        
        role = profile.role
        user = profile.user  # Get the User object from the Profile

        if role == 'admin':
            return Appointment.objects.all()  # Admins see all appointments
        elif role == 'staff':
            return Appointment.objects.filter(staff=user)  # Staff see their assigned appointments
        elif role == 'client':
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
        
        # Parse and validate the date field for MM-DD-YYYY format
        date = self.request.data.get("date")
        if isinstance(date, str):
            try:
                # Convert MM-DD-YYYY to YYYY-MM-DD
                parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                try:
                    # If that fails, try MM-DD-YYYY
                    parsed_date = datetime.strptime(date, "%m-%d-%Y").date()
                except ValueError:
                    raise ValidationError({"date": "Date must be in MM-DD-YYYY format."})
            serializer.save(user=user, date=parsed_date)  # Save with parsed date
        else:
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
        profile = validate_token(self.request)  # Returns a Profile object
        if not profile:
            raise PermissionDenied("User profile not found.")
        
        user = profile.user
        role = role = profile.role

        if role == 'admin':
            return Appointment.objects.all()  # Admins see all appointments
        elif role == 'staff':
            return Appointment.objects.filter(staff=user)  # Staff see their assigned appointments
        elif role == 'client':
            return Appointment.objects.filter(user=user)  # Clients see their own appointments
        return Appointment.objects.none()  # Default to no access if role is undefined
    
    def put(self, request, *args, **kwargs):
        """
        Override PUT to log details and call the parent method.
        """
        appointment_id = kwargs.get("pk")  # Get the appointment ID from the URL
        print("Updating Appointment ID:", appointment_id) # Debugging
        print("Request Data:", request.data) # Debugging the payload

        # Call the parent PUT method to perform the update
        return super().put(request, *args, **kwargs)

# Path to your Firebase credentials JSON file
try:
    get_app()
except ValueError:
    cred = credentials.Certificate("C:/Users/Vince/Documents/GitHub/appointment-scheduler/healthcare-backend/backend/firebase/firebase-adminsdk.json")
    initialize_app(cred)

print("Firebase Initialized Successfully")
        