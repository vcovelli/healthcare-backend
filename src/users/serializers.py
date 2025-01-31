from rest_framework import serializers
from src.users.models import Profile
from src.core.utils import validate_phone_number_format, validate_unique_email

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'firebase_uid', 'user']
        extra_kwargs = {
            'firebase_uid': {'read_only': True},
            'user': {'read_only': True},  # Prevent modifying user field
        }

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
