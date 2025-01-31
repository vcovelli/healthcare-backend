from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from src.users.models import Profile
import logging

logger = logging.getLogger(__name__)

# Signal to automatically create or update the Profile model whenever a User is created or saved
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile for a new user if it doesn't already exist.
    """
    if created:
        email = instance.email if instance.email else f"{instance.username}@example.com"

        if not email or email == "default@example.com":
            raise ValueError("Missing email during user creation!")

        Profile.objects.create(
            user=instance,
            email=email,
            firebase_uid=instance.username,
            role='client',
            profile_completed=False
        )

        print(f"Profile created for {email}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):  
    if hasattr(instance, 'profile'):  
        instance.profile.save()



class Appointment(models.Model):
    title = models.CharField(max_length=225)
    date = models.DateField(default=now) # Set a default date
    time = models.TimeField(default=now) # Set a default time
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    staff = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="staff_appointments"
    )

    def __str__(self):
        return f"Appointment: {self.title} on {self.date} at {self.time}"
    
    # Method to get the user's role safely
    @property
    def user_role(self):
        try:
            return self.user.profile.role
        except AttributeError:
            return "unknown"
