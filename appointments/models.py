from django.db import models

class Appointment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
