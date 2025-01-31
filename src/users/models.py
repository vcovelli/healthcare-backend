from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=False, blank=False, default="example@example.com")
    
    phone_number = models.CharField(
        max_length=15,
        null=True, blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )
    
    firebase_uid = models.CharField(max_length=255, unique=True, null=False, blank=False)  # Add Firebase UID field
    role = models.CharField(max_length=50, default='client')
    profile_completed = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username