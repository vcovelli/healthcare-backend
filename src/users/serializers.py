from rest_framework import serializers
from src.users.models import Profile
from src.core.utils import validate_phone_number_format, validate_unique_email

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'firebase_uid', 'user', 'profile_completed']
        extra_kwargs = {
            'firebase_uid': {'read_only': True},
            'user': {'read_only': True},  # Prevent modifying the user field
            'email': {'read_only': True},  # Email will be auto-populated from the Firebase user
            'profile_completed': {'read_only': True},  # Auto-updated based on form completion
        }

    def update(self, instance, validated_data):
        """
        Update the profile and automatically set `profile_completed` to True
        if all required fields are filled.
        """
        # Update the instance with validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Check if all required fields are filled and set `profile_completed` to True
        required_fields = ['first_name', 'last_name', 'phone_number']
        if all(getattr(instance, field) for field in required_fields):
            instance.profile_completed = True

        instance.save()
        return instance

    def validate_phone_number(self, value):
        return validate_phone_number_format(value)
    
    def validate_email(self, value):
        return validate_unique_email(value, self.instance)

    def update(self, instance, validated_data):
        """Ensure all updates are properly handled"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
