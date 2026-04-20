from django.contrib import admin
from django.urls import path, include
from .views import home_view  # Importing the home_view from config/views.py

# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('communications/', include('communications.urls')), # No namespace here!
    path('', home_view, name='home'),
]