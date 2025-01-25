from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('client', 'Client'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Add Firebase UID field

    def __str__(self):
        return f"{self.user.username} - {self.role}"