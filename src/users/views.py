from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated
from rest_framework import generics, permissions, status
from firebase_admin.auth import get_user
from firebase_admin import auth as firebase_auth
from django.contrib.auth.models import User

from src.users.models import Profile
from src.users.serializers import ProfileSerializer

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

class UpdateProfileView(generics.RetrieveUpdateAPIView):
    """
    API View for clients to retrieve and update their profiles.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Fetch the profile to update based on the logged-in user or the provided primary key.
        """
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")

        pk = self.kwargs.get('pk')
        if pk:
            try:
                return Profile.objects.get(pk=pk)
            except Profile.DoesNotExist:
                raise NotAuthenticated("Profile not found.")
        return self.request.user.profile
    
    def patch(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Missing or invalid Authorization header"}, status=403)

        token = auth_header.split("Bearer ")[1]

        try:
            # Verify the Firebase token
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token["uid"]

            # Fetch the user's profile
            profile = Profile.objects.get(firebase_uid=uid)

            # Populate the email field if it doesn't exist
            if not profile.email:
                profile.email = decoded_token.get("email", "")
                profile.save()

            # Update the profile with the provided data
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
