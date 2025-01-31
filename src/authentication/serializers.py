from rest_framework import serializers

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
    