from django.urls import path
from . import views

urlpatterns = [
    # This maps to http://127.0.0.1:8000/communications/
    path('', views.communications_list, name='communications_list'),
]