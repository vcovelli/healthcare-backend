from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from firebase_admin import auth as firebase_auth
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.decorators import api_view, permission_classes
from .serializers import LoginSerializer, FirebaseTokenSerializer
from src.users.models import Profile
import time
from src.core.utils import validate_token
from django.http import JsonResponse

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Returns the profile of the authenticated user.
    """
    auth_header = request.headers.get("Authorization")
    print(f"Authorization Header: {auth_header}")  # Debugging
    
    if not auth_header or not auth_header.startswith("Bearer "):
        print("Missing or invalid Authorization header")
        return JsonResponse({"error": "Missing or invalid Authorization header"}, status=403)

    token = auth_header.split("Bearer ")[1]
    print(f"Received Firebase Token: {token}")  # Debugging

    try:
        decoded_token = firebase_auth.verify_id_token(token)
        uid = decoded_token["uid"]
        print(f"Firebase UID: {uid}")

        # Fetch user profile
        profile = Profile.objects.get(firebase_uid=uid)
        print(f"Profile found for UID: {uid}")

        return JsonResponse({
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "email": profile.email,
            "phone_number": profile.phone_number,
            "role": profile.role,
            "profile_completed": profile.profile_completed
        })
    except Profile.DoesNotExist:
        print(f"No profile found for UID: {uid}")
        return JsonResponse({"error": "User profile not found"}, status=404)
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return JsonResponse({"error": "Invalid Firebase token"}, status=403)

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
            clock_skew = 60  # Allow 60 seconds of clock skew
            if issued_at > current_time + clock_skew or expiration_time < current_time - clock_skew:
                raise AuthenticationFailed("Firebase Authentication failed: Token used outside the allowed time window.")

            # Extract user information
            user_id = decoded_token.get('uid')
            email = decoded_token.get('email')
            if not email:
                raise AuthenticationFailed("Email not found in Firebase token.")

            print("UID:", user_id, "Email:", email)  # Debug: Print UID and email
            
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
            print("Error during authentication:", str(e))  # Debug: Print errors
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Missing or invalid Authorization header"}, status=403)

        token = auth_header.split("Bearer ")[1]
        print(f"Received Firebase Token: {token}")  # Debugging

        try:
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token["uid"]
            print(f"Firebase UID: {uid}")

            # Fetch user profile from database
            try:
                profile = Profile.objects.get(firebase_uid=uid)
                return Response({"role": profile.role})
            except Profile.DoesNotExist:
                print("No profile found for this Firebase UID.")
                return Response({"error": "User profile not found"}, status=404)

        except Exception as e:
            print(f"Error verifying Firebase token: {e}")
            return Response({"error": "Invalid Firebase token"}, status=403)
