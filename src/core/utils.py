from rest_framework.exceptions import PermissionDenied
from firebase_admin import auth as firebase_auth
from src.users.models import Profile
from django.core.exceptions import MultipleObjectsReturned

def validate_token(request):
    # Ensure Authorization header exists
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        print("Authorization header is missing")
        raise PermissionDenied("Missing Authorization header")

    # Ensure header starts with "Bearer"
    if not auth_header.startswith("Bearer "):
        print("Invalid Authorization header format")
        raise PermissionDenied("Invalid Authorization header format")

    # Extract token
    token = auth_header.split(" ")[1]

    # Validate token
    try:
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)
        print("Decoded Token:", decoded_token)  # Debugging
        firebase_uid = decoded_token.get("uid")
        if not firebase_uid:
            raise PermissionDenied("Firebase UID not found in token")

        # Fetch user profile
        try:
            profile = Profile.objects.get(firebase_uid=firebase_uid)
        except Profile.DoesNotExist:
            print(f"No Profile found for UID: {firebase_uid}")
            raise PermissionDenied(f"Profile not found for UID: {firebase_uid}")
        except MultipleObjectsReturned:
            print(f"Multiple profiles found for UID: {firebase_uid}")
            raise PermissionDenied("Multiple profiles found for the same UID. Please contact support.")

        print(f"Validated Profile: {profile.user.username} - {profile.role}")  # Debugging
        return profile
    except firebase_auth.InvalidIdTokenError:
        raise PermissionDenied("Invalid Firebase token")
    except firebase_auth.ExpiredIdTokenError:
        raise PermissionDenied("Expired Firebase token")
    except firebase_auth.RevokedIdTokenError:
        raise PermissionDenied("Revoked Firebase token")
    except Exception as e:
        print("Unexpected validation error:", str(e))
        raise PermissionDenied("Unexpected error during token validation")