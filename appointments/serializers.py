from rest_framework import serializers
from .models import Appointment
from django.utils import timezone

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate_date_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Date and time must be in the future.")
        return value        