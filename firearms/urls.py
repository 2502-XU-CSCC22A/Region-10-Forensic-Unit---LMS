from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='firearms_home'),
]