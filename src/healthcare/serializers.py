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
        fields = ['id', 'title', 'date', 'time', 'user', 'staff']

    def validate(self, data):
        # Parse and validate the date
        data['date'] = parse_and_validate_date(data['date'])

        # Validate future date and time
        validate_future_date_time(data['date'], data['time'])

        return data
    
