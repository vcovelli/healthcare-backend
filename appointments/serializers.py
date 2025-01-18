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
        date_time = timezone.make_aware(
            timezone.datetime.combine(data['date'], data['time']),
            timezone.get_current_timezone()
        )
        if date_time <= timezone.now():
            raise serializers.ValidationError("The appointment date and time must be in the future.")
        return data   