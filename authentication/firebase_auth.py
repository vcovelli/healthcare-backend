import firebase_admin
from firebase_admin import auth, credentials
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

# Initialize Firebase Admin
cred = credentials.Certificate("path/to/your/firebase-adminsdk.json")  # Replace with your Firebase service account key
firebase_admin.initialize_app(cred)

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            token = auth_header.split(' ')[1]
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
        except Exception as e:
            raise AuthenticationFailed(f'Firebase Authentication failed: {str(e)}')

        try:
            user, created = User.objects.get_or_create(username=uid)
            return (user, None)
        except Exception as e:
            raise AuthenticationFailed(f'User creation failed: {str(e)}')
