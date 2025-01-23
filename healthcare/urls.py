from django.urls import path
from .views import ( 
    AppointmentListCreateView,
    AppointmentDetailView,
    CreateProfileView,
    ProfileView,
)
from authentication.views import LoginView  # Import LoginView from authentication app

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('profiles/', ProfileView.as_view(), name='profile'),
    path('profiles/create/', CreateProfileView.as_view(), name='create-profile'),
    path('login/', LoginView.as_view(), name='login'),
]