from rest_framework import serializers
from .models import Appointment
from django.utils import timezone
from datetime import datetime

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        # Combine date and time fields to validate full datetime
        appointment_datetime = datetime.combine(data['date'], data['time'])

        if appointment_datetime < timezone.now():
            raise serializers.ValidationError("The date and time must be in the future.")
        
        return data       