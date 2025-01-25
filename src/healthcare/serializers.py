from rest_framework import serializers
from .models import Appointment, Profile
from django.utils import timezone
from datetime import datetime

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'role']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'title', 'date', 'time']

    def validate(self, data):
        # Parse date if it is in MM-DD-YYYY format
        if isinstance(data['date'], str):
            try:
                # Convert MM-DD-YYYY to YYYY-MM-DD
                data['date'] = datetime.strptime(data['date'], "%m-%d-%Y").date()
            except ValueError:
                raise serializers.ValidationError({"date": "Date must be in MM-DD-YYYY format."})

        # Combine date and time for validation
        date_time = timezone.make_aware(
            timezone.datetime.combine(data['date'], data['time']),
            timezone.get_current_timezone()
        )
        if date_time <= timezone.now():
            raise serializers.ValidationError("The appointment date and time must be in the future.")

        return data   