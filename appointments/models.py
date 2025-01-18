from django.db import models
from django.utils.timezone import now

class Appointment(models.Model):
    title = models.CharField(max_length=225)
    date = models.DateField(default=now) # Set a default date
    time = models.TimeField(default=now) # Set a default time
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, default=1) # Default to user with ID 1

    def __str__(self):
        return self.title
