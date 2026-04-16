from django.contrib import admin
from django.urls import path
from django.urls import path
from django.shortcuts import render
from django.views.generic import TemplateView
<<<<<<< Updated upstream
from django.urls import path, include
from .views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('disposal/', include('disposal.urls')),
    
    path('', home_view, name='home'), 
]
=======
from communications.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
>>>>>>> Stashed changes
]
