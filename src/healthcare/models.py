from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from src.users.models import Profile
from firebase_admin import auth as firebase_auth
import firebase_admin
import logging

logger = logging.getLogger(__name__)

# Signal to automatically create or update the Profile model whenever a User is created or saved
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a profile for a new user if it doesn't already exist.
    """
    if created:
        try:
            # Retrieve the Firebase user data using the UID stored in username
            firebase_user = firebase_auth.get_user(instance.username)
            email = firebase_user.email  # Get the real email from Firebase
        except firebase_admin.auth.UserNotFoundError:
            print(f"Firebase user not found for UID: {instance.username}")
            email = instance.email  # Fallback to Django's email field

        if not email or email == "default@example.com":
            raise ValueError("Missing email during user creation!")

        profile = Profile.objects.create(
            user=instance,
            email=email,  # Ensure it stores the real email
            firebase_uid=instance.username,
            role='client',
            profile_completed=False
        )

        print(f"Profile created for {email}")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):  
    """
    Ensure profile is saved when the user is updated and mark profile as complete.
    """
    if hasattr(instance, 'profile'):  
        profile = instance.profile

        # Ensure the correct email is stored in the profile
        try:
            firebase_user = firebase_auth.get_user(instance.username)
            profile.email = firebase_user.email  # Sync email with Firebase
        except firebase_admin.auth.UserNotFoundError:
            print(f"Firebase user not found for UID: {instance.username}")

        # Check if all required fields are filled
        required_fields = ['first_name', 'last_name', 'phone_number']
        if all(getattr(profile, field, None) for field in required_fields):
            profile.profile_completed = True  # Set profile_completed to True
            print(f"Profile completed for {profile.email}")

        profile.save()



class Appointment(models.Model):
    title = models.CharField(max_length=225)
    appointment_date = models.DateTimeField() # Set a default date
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
    status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment: {self.title} on {self.date} at {self.time}"
    
    # Method to get the user's role safely
    @property
    def user_role(self):
        try:
            return self.user.profile.role
        except AttributeError:
            return "unknown"
