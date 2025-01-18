from rest_framework import serializers
from .models import Appointment
from django.utils import timezone
from datetime import datetime

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        date_time = timezone.make_aware(
            timezone.datetime.combine(data['date'], data['time']),
            timezone.get_current_timezone()
        )
        if date_time <= timezone.now():
            raise serializers.ValidationError("The appointment date and time must be in the future.")
        return data   