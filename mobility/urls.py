from django.urls import path
from . import views

app_name = 'mobility'

urlpatterns = [

    # VEHICLE MANAGEMENT
    path(
        'management/',
        views.vehicle_management,
        name='vehicle_management'
    ),

    path(
        'edit/<int:pk>/',
        views.edit_vehicle,
        name='edit_vehicle'
    ),

    path(
        'vehicle/delete/<int:pk>/',
        views.delete_vehicle,
        name='delete_vehicle'
    ),

    # PAR MONITORING
    path(
        'par/',
        views.par_management,
        name='par_management'
    ),

    path(
        'par/delete/<int:pk>/',
        views.delete_par,
        name='delete_par'
    ),

    path(
        'par/print/<int:pk>/',
        views.print_par,
        name='print_par'
    ),

    # ACTIVITY LOG
    path(
        'activity/',
        views.activity_log,
        name='activity_log'
    ),

    # EMAIL ALERTS
    path(
        'send-alerts/',
        views.manual_email_alert,
        name='manual_email_alert'
    ),
path('vehicle/<int:pk>/mark-ber/', views.mark_vehicle_ber, name='mark_vehicle_ber'),
path('vehicle/<int:pk>/send-disposal/', views.send_vehicle_to_disposal, name='send_vehicle_to_disposal'),
path('par/edit/<int:pk>/', views.edit_par, name='edit_par'),

]