from django.db import models

class Appointment(models.Model):
    title = models.CharField(max_length=225)
    date = models.DateField()
    time = models.TimeField()
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
