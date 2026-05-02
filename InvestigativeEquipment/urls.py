from django.urls import path
from . import views

app_name = "InvestigativeEquipment"

urlpatterns = [
    # The main page that lists everything
    path('', views.investigative_view, name='investigative_view'),
    
    # Specific endpoints for the Modals
    path('add/', views.investigative_view, name='investigative_add'),
    path('update/', views.investigative_view, name='investigative_update'),
    path('delete/', views.investigative_view, name='investigative_delete'),
]