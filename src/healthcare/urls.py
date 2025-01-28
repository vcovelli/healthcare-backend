from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView
from src.authentication.views import CreateProfileView, ProfileView

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'), # List/create appointments
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'), # Appointment details
    path('profiles/', ProfileView.as_view(), name='profile'), # Profile list
    path('profiles/create/', CreateProfileView.as_view(), name='create-profile'), # Create profile
]