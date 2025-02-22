from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'), # List/create appointments
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'), # Appointment details
]