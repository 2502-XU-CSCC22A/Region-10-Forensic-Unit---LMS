from django.contrib import admin
from django.urls import path, include
from .views import home_view  # Importing the home_view from config/views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This connects your communications app
    path('communications/', include('communications.urls')),
    
    # This handles the root URL (127.0.0.1:8000/)
    path('', home_view, name='home'),
]