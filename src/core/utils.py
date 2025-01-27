from rest_framework.exceptions import PermissionDenied
from firebase_admin import auth as firebase_auth
from src.users.models import Profile

def validate_token(request):
    auth_header = request.headers.get("Authorization", "")
    print(f"Authorization Header: {auth_header}")  # Debugging
    if not auth_header.startswith("Bearer "):
        print("Missing or invalid Authorization header")
        raise PermissionDenied("Invalid Authorization header format")

    token = auth_header.split(" ")[1]
    try:
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)  # Decode the token
        print("Decoded Token:", decoded_token)  # Debugging
        firebase_uid = decoded_token.get("uid")
        if not firebase_uid:
            raise PermissionDenied("Firebase UID not found in token")

        profile = Profile.objects.filter(firebase_uid=firebase_uid).first()
        if not profile:
            print(f"No Profile found for UID: {firebase_uid}")  # Debugging
            raise PermissionDenied(f"Profile not found for UID: {firebase_uid}")
        
        print(f"Validated Profile: {profile.user.username} - {profile.role}")  # Debugging
        return profile
    except Exception as e:
        print("Token Validation Error:", str(e))
        raise PermissionDenied("Invalid or expired token")