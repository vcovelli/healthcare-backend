from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from src.users.models import Profile

    
# Signal to automatically create or update the Profile model whenever a User is created or saved
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):  # Avoid duplicate creation
        firebase_uid = instance.username  # Assuming Firebase UID is stored in `username`
        Profile.objects.create(user=instance, role='client', firebase_uid=firebase_uid)

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
