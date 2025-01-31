from django.urls import path
from src.users.views import ProfileView, UpdateProfileView, CreateProfileView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path("profile/update/<str:pk>", UpdateProfileView.as_view(), name="update-profile"),  # Allow updating profile
    path("profile/update/", UpdateProfileView.as_view(), name="update-profile-self"),
    path("profile/create/", CreateProfileView.as_view(), name="create-profile"),
]
