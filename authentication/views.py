from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from firebase_admin import auth as firebase_auth
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed, NotFound
from .serializers import LoginSerializer, FirebaseTokenSerializer
from healthcare.models import Profile
import time

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