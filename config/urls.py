# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import render
from .views import home_view
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
 
    # ── Feature Pages ─────────────────────────────────────────────────────────────
    path('mobility/', include('mobility.urls')),
   

    
]