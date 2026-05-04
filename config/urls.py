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
    path('disposal/', include('disposal.urls'), name='disposal'),
    #path('login/', include ('login.urls'), name='login'),
    path('mobility/', include('mobility.urls'), name='mobility'),
   

    
]