from django.urls import path
from . import views

app_name = 'mobility'

urlpatterns = [
    # Main Dashboard & Detailed List
    path('', views.vehicle_management, name='vehicle_management'),
    path('vehicles/detailed/', views.vehicle_list_detailed, name='vehicle_list_detailed'),
    
    # Vehicle Actions (Edit/Delete)
    path('edit/<int:pk>/', views.edit_vehicle, name='edit_vehicle'),
    path('vehicle/delete/<int:pk>/', views.delete_vehicle, name='delete_vehicle'),
    
    # PAR Management
    path('par/', views.par_management, name='par_management'),
    path('par/delete/<int:pk>/', views.delete_par, name='delete_par'),
    path('par/print/<int:pk>/', views.print_par, name='print_par'),
    
    # Alerts & Logging
    path('activity/', views.activity_log, name='activity_log'),
    # Note: Only one 'send-alerts' path using the manual_email_alert view
    path('send-alerts/', views.manual_email_alert, name='manual_email_alert'),
]