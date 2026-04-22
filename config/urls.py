from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static  # ADD THIS
##from .views import home_view
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('usermanagement.urls')),
    path('usermanagement/', include('usermanagement.urls')), 
]