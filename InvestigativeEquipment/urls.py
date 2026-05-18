from django.urls import path
from . import views
 
app_name = 'InvestigativeEquipment'
 
urlpatterns = [
    # Main inventory page
    path('', views.investigative_view, name='investigative_view'),
 
    # Investigative Equipment CRUD
    path('add/', views.investigative_view, name='investigative_add'),
    path('update/', views.investigative_view, name='investigative_update'),
    path('investigative/move-to-ber/<int:item_id>/', views.move_to_ber_investigative, name='move_to_ber_investigative'),    
    path('reports/', views.activity_logs, name="activity_logs"),
    
    # PAR Monitoring
    path('par-monitoring/', views.par_monitoring_view, name='par_monitoring'),
    path('par-monitoring/<int:pk>/edit/', views.edit_par_view, name='edit_par'),
    path('par-monitoring/<int:pk>/delete/', views.delete_par_view, name='delete_par'),
    path('par-monitoring/<int:pk>/print/', views.print_par_view, name='print_par'),
 
    # ICS Monitoring
    path('ics-monitoring/', views.ics_monitoring_view, name='ics_monitoring'),
    path('ics-monitoring/<int:pk>/edit/', views.edit_ics_view, name='edit_ics'),
    path('ics-monitoring/<int:pk>/delete/', views.delete_ics_view, name='delete_ics'),
    path('ics-monitoring/<int:pk>/print/', views.print_ics_view, name='print_ics'),
]
 