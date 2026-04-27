from django.contrib import admin
from django.urls import path
from django.urls import path
from django.shortcuts import render
from django.views.generic import TemplateView
from django.urls import path, include
from .views import home_view
from config import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'), 
    path('investigative/', include('InvestigativeEquipment.urls')),
]
