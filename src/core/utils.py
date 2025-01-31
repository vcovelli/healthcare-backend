from rest_framework.exceptions import PermissionDenied
from firebase_admin import auth as firebase_auth
from src.users.models import Profile
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from datetime import datetime
from rest_framework.exceptions import ValidationError
from rest_framework import serializers

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
        
        # Assign the corresponding user to the request
        request.user = profile.user  # Set the authenticated user for the request
        print(f"Request User Set Inside validate_token: {request.user}")  # Debugging

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
    
def parse_and_validate_date(date_str):
    """
    Parses a date string and ensures it's in the correct format (MM-DD-YYYY or YYYY-MM-DD).
    Returns a valid date object.
    """
    if isinstance(date_str, str):
        try:
            # Try YYYY-MM-DD first
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                # Fall back to MM-DD-YYYY
                return datetime.strptime(date_str, "%m-%d-%Y").date()
            except ValueError:
                raise ValidationError({"date": "Date must be in MM-DD-YYYY or YYYY-MM-DD format."})
    return date_str


def validate_future_date_time(date, time):
    """
    Combines date and time, and checks if the result is in the future.
    """
    date_time = timezone.make_aware(
        timezone.datetime.combine(date, time),
        timezone.get_current_timezone()
    )
    if date_time <= timezone.now():
        raise ValidationError("The appointment date and time must be in the future.")
    
def validate_profile_data(first_name, last_name, phone_number):
    """
    Validates profile data for required fields.
    """
    errors = {}

    if not first_name or not first_name.strip():
        errors['first_name'] = "First name is required."

    if not last_name or not last_name.strip():
        errors['last_name'] = "Last name is required."

    if not phone_number or not phone_number.strip():
        errors['phone_number'] = "Phone number is required."

    if errors:
        raise ValidationError(errors)
    
def validate_phone_number_format(value):
    """
    Validate phone number format.
    """
    import re
    if not re.match(r"^\+?1?\d{9,15}$", value):
        raise serializers.ValidationError(
            "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )
    return value

def validate_unique_email(value, instance=None):
    """
    Validate email is unique across profiles.
    """
    from src.healthcare.models import Profile  # Import here to avoid circular imports
    if Profile.objects.filter(email=value).exclude(id=instance.id if instance else None).exists():
        raise serializers.ValidationError("A profile with this email already exists.")
    return value