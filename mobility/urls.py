from django.urls import path
from . import views

app_name = 'mobility'

urlpatterns = [
    # Main Dashboard & Detailed List
    path('', views.vehicle_management, name='vehicle_management'),
    path('vehicles/detailed/', views.vehicle_list_detailed, name='vehicle_list_detailed'),
    
    # Vehicle Actions
    path('edit/<int:pk>/', views.edit_vehicle, name='edit_vehicle'),
    
    # PAR Management
    path('par/', views.par_management, name='par_management'),
    path('par/edit/<int:pk>/', views.edit_par, name='edit_par'),
    path('par/print/<int:pk>/', views.print_par, name='print_par'),
    path('par/archive/<int:pk>/', views.archive_par, name='archive_par'), 
    
    path('vehicle/<int:pk>/dispose/', views.move_vehicle_to_disposal, name='move_vehicle_to_disposal'),
    
    # Alerts & Logging
    path('activity/', views.activity_log, name='activity_log'),
    path('send-alerts/', views.manual_email_alert, name='manual_email_alert'),
]