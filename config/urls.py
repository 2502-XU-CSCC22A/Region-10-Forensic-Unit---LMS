# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mobility/', include('mobility.urls')), # Dashboard will be at /mobility/
]