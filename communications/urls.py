from django.urls import path
from . import views

urlpatterns = [
    path('', views.communications_list, name='communications_list'),
    path('add/', views.add_communication_view, name='add_communication'),
]