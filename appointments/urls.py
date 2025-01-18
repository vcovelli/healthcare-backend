from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView, CreateProfileView

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('profiles/', CreateProfileView.as_view(), name='create-profile'),
]