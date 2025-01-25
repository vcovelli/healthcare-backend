from rest_framework import serializers
from src.users.models import Profile

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if not data.get("email") or not data.get("password"):
            raise serializers.ValidationError("Both email and password are required.")
        return data
    
class FirebaseTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("Firebase token is required.")
        # Further Firebase-specific validation can be added here if necessary.
        return value
    
class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
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