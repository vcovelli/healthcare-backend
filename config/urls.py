"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.http import HttpResponse  # Add this line
from django.contrib import admin  # Add this line
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls), # Admin panel
    path("api/", include("src.healthcare.urls")), # Healthcare app endpoints
    path('api/auth/', include('src.authentication.urls')),  # Authentication endpoints
    path('api/users/', include('src.users.urls')), 
    path("", lambda request: HttpResponse("Welcome to the Healthcare Appointments API!")),
]

# Serve static files in development
if settings.DEBUG:  # Only do this in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)