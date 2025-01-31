from django.contrib import admin
from .models import Profile, Appointment

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'firebase_uid')  # Columns to display
    search_fields = ('user__username', 'role', 'firebase_uid')  # Enable search
    list_filter = ('role',)  # Add filter options

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment_date", "title", "user", "staff", "status")  # Columns to display
    search_fields = ('title', 'user__username')  # Enable search
    list_filter = ("appointment_date",)  # Add filter options
