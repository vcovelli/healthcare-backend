from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from firebase_admin import auth as firebase_auth
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.decorators import api_view, permission_classes
from .serializers import LoginSerializer, FirebaseTokenSerializer, ProfileSerializer
from src.users.models import Profile
import time
from src.core.utils import validate_token
from firebase_admin.auth import get_user

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_user_role(request):
    print(f"Authenticated User: {request.user}")  # Debugging
    profile = validate_token(request)
    return Response({"role": profile.role}, status=status.HTTP_200_OK)

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

class LoginView(APIView):
    """
    API view to validate Firebase token, create Django User and Profile if needed, and return user details.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Log the incoming request headers
        print("Request Headers:", request.headers)

        # Extract the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            print("Authorization header missing or invalid.")
            raise AuthenticationFailed("Authorization header missing or invalid.")
        
        token = auth_header.split(" ")[1]  # Extract the token
        print("Firebase Token:", token)

        try:
            # Verify the Firebase token
            decoded_token = firebase_auth.verify_id_token(token) 
            print("Decoded Token:", decoded_token)  # **Debug: Print decoded token**

            # Allowing a clock skew of 60 seconds during token verification
            current_time = time.time()
            issued_at = decoded_token.get('iat', 0)
            expiration_time = decoded_token.get('exp', 0)

            # Check for token validity with clock skew
            clock_skew = 60  # Allow 60 seconds of clock skew
            if issued_at > current_time + clock_skew or expiration_time < current_time - clock_skew:
                raise AuthenticationFailed("Firebase Authentication failed: Token used outside the allowed time window.")

            user_id = decoded_token.get('uid')
            email = decoded_token.get('email')

            print("UID:", user_id, "Email:", email)  # **Debug: Print UID and email**

            if not email:
                raise AuthenticationFailed("Email not found in Firebase token.")
            
            # Check if the user already exists
            user, created = User.objects.get_or_create(
                username=user_id,
                defaults={'email': email}
            )
            print(f"User {'created' if created else 'exists'}: {user.username}")
            
            # Create a profile if it doesn't exist
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults={'role': 'client'}
            )
            print(f"Profile {'created' if profile_created else 'exists'}: {profile.role}")
            

            # Return success response
            return Response({
                "message": "Login successful",
                "user_id": user_id,
                "email": email,
                "role": profile.role,
            })

        except Exception as e:
            print("Error during authentication:", str(e))  # **Debug: Print errors**
            raise AuthenticationFailed(f"Firebase Authentication failed: {str(e)}")
        
class VerifyFirebaseTokenView(APIView):
    """
    View to verify the Firebase token.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = FirebaseTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract the token from the validated data
        token = serializer.validated_data.get("token")

        try:
            decoded_token = firebase_auth.verify_id_token(token)
            firebase_uid = decoded_token.get("uid")

            # Check if the user exists in the Django database
            user = User.objects.filter(username=firebase_uid).first()
            if user:
                return Response({"message": "Token is valid.", "user_id": user.id}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        except ValueError:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RoleView(APIView):
    """
    View to retrieve the role of the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        try:
            # Retrieve the role from the associated Profile model
            role = user.profile.role
            return Response({"role": role}, status=200)
        except AttributeError:
            raise NotFound("User profile not found. Role cannot be determined.")