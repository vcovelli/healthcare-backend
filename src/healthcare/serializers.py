from rest_framework import serializers
from src.healthcare.models import Appointment
from src.users.models import Profile
from src.core.utils import ( 
    parse_and_validate_date,
    validate_future_date_time,
    )

class AppointmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Fix field name from `client` to `user`
    staff = serializers.StringRelatedField()
    class Meta:
        model = Appointment
        fields = ['id', 'title', 'appointment_date', 'time', 'user', 'staff', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        validated_data = data.copy()
        
        # Parse and validate the date
        validated_data['appointment_date'] = parse_and_validate_date(validated_data['appointment_date'])

        # Validate future date and time
        validate_future_date_time(validated_data['appointment_date'], validated_data['time'])

        return validated_data
    
