from django.urls import path
from .views import ( 
    LoginView,
    VerifyFirebaseTokenView,
    RoleView,
    get_user_profile,

)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'), # Login
    path('verify-token/', VerifyFirebaseTokenView.as_view(), name='verify-token'), # Token verification
    path("role/", RoleView.as_view(), name="role"), # Role endpoint
    path("profile/detail/", get_user_profile, name="get_user_profile"),
]