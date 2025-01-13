from django.urls import path
from .views import AppointmentListCreateView, AppointmentDetailView

urlpatterns = [
    path("", AppointmentListCreateView.as_view(), name="appointment_list_create"),
    path("<int:pk>/", AppointmentDetailView.as_view(), name="appointment_detail"),
]