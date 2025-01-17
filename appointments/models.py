from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Define role choices for users
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('staff', 'Staff'),
    ('client', 'Client'),
]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
# Signal to automatically create or update the Profile model whenever a User is created or saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, role='client')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):    
    instance.profile.save()



class Appointment(models.Model):
    title = models.CharField(max_length=225)
    date = models.DateField(default=now) # Set a default date
    time = models.TimeField(default=now) # Set a default time
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE) # Link to the User model

    def __str__(self):
        return self.title
    
    # Method to get the user's role
    @property
    def user_role(self):
        return self.user.profile.role
