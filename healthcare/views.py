from rest_framework import generics, permissions, status, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Appointment, Profile
from .serializers import AppointmentSerializer, ProfileSerializer
from django.contrib.auth.models import User
from firebase_admin import auth as firebase_auth, credentials, initialize_app, get_app
from firebase_admin.auth import get_user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'role', 'firebase_uid']
        extra_kwargs = {
            'firebase_uid': {'read_only': True},  # This will be set programmatically
            'user': {'read_only': True},  # Exclude 'user' from being required in request.data
        }

    def create(self, validated_data):
        # Remove the password from the validated data to avoid saving it as plain text
        password = validated_data.pop('password', None)
        profile = super().create(validated_data)

        # Set the password (hashed) on the user object
        if password:
            profile.user.set_password(password)
            profile.user.save()

        return profile

# Custom permission to handle role-based access
class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to allow:
    - Admins to view and manage all appointments.
    - Staff to view and manage appointments related to them.
    - Clients to only view and manage their own appointments.
    """

    def has_object_permission(self, request, view, obj):
        role = request.user.profile.role
        if role == 'admin':
            return True  # Admins can access everything
        elif role == 'staff':
            return obj.staff == request.user # Staff can access appointments associated with them
        elif role == 'client': 
            return obj.user == request.user # Clients can only access their own appointments
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
        role = user.profile.role

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
        role = user.profile.role

        if role == 'admin':
            return Appointment.objects.all()  # Admins see all appointments
        elif role == 'staff':
            return Appointment.objects.filter(staff=user)  # Staff see their assigned appointments
        elif role == 'client':
            return Appointment.objects.filter(user=user)  # Clients see their own appointments
        return Appointment.objects.none()  # Default to no access if role is undefined

# Path to your Firebase credentials JSON file
try:
    get_app()
except ValueError:
    cred = credentials.Certificate("C:/Users/Vince/Documents/GitHub/appointment-scheduler/healthcare-backend/backend/firebase/firebase-adminsdk.json")
    initialize_app(cred)

print("Firebase Initialized Successfully")

# View for creating user profiles
class CreateProfileView(APIView):
    """
    API view to create user profiles.
    Only admins can create profiles for other users.
    """
    permission_classes = [permissions.IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        try:
            # Log headers and payload
            print("Request recieved at CreateProfileView")
            print("Request Data:", request.data)

            # Extract and verify Firebase token
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return Response({"error": "Invalid Authorization header format"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract and verify Firebase token from the Authorization header
            token = auth_header.split(" ")[1]
            decoded_token = firebase_auth.verify_id_token(token)
            firebase_uid = decoded_token.get("uid")
            print("Decoded Token:", decoded_token)

            # Check email verification status
            firebase_user = get_user(firebase_uid)
            if not firebase_user.email_verified:
                return Response({"error": "Please verify your email before logging in."}, status=status.HTTP_400_BAD_REQUEST)

            # Extract email, password, and role from request data
            email = request.data.get("email")
            password = request.data.get("password")
            role = request.data.get("role", "client")  # Default role is 'client'

            if not email or not password:
                return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user already exists
            if User.objects.filter(username=firebase_uid).exists():
                return Response(
                    {"error": "A user with this Firebase UID already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create Django user
            new_user = User.objects.create_user(
                username=firebase_uid, # Firebase UID as the username
                password=password,
                email=email,
            )

            # Create profile
            profile = Profile.objects.create(
                user=new_user,
                role=role,
                firebase_uid=firebase_uid,
            )

            # Validate the request data and create the profile
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        except ValueError as e:
            print("Firebase Authentication Error:", str(e))  # Debug log for Firebase auth errors
            return Response({"error": f"Firebase validation error: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print("General Error:", str(e))  # Debug log for general errors
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)
        
class ProfileView(APIView):
    """
    API view to retrieve the logged-in user's profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Fetch the profile for the logged-in user
            profile = request.user.profile  # Assuming a OneToOneField relationship to Profile
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("General Error:", str(e))  # Debug log for general errors
            return Response({"error": "An unexpected error occurred. Please try again later."},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


