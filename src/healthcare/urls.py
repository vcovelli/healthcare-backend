from django.urls import path
from .views import ( 
    AppointmentListCreateView,
    AppointmentDetailView,
)
from src.authentication.views import LoginView  # Import LoginView from authentication app
from src.authentication.views import get_user_role
from src.authentication.views import CreateProfileView, ProfileView

urlpatterns = [
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('profiles/', ProfileView.as_view(), name='profile'),
    path('profiles/create/', CreateProfileView.as_view(), name='create-profile'),
    path('auth/role/', get_user_role, name='get_user_role'),
]