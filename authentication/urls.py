from django.urls import path
from .views import LoginView, VerifyFirebaseTokenView, RoleView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('verify-token/', VerifyFirebaseTokenView.as_view(), name='verify-token'),
    path("role/", RoleView.as_view(), name="role"),
]