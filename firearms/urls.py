from django.urls import path  
from . import views

app_name = 'firearms'

urlpatterns = [
  
    path('', views.index, name='index'), 
    
    path('management/', views.par_management, name='par_management'),
    
    # Firearm API endpoints
    path('api/list/',            views.firearm_list,    name='api_list'),
    path('api/create/',          views.firearm_create,  name='firearm_create'),
    path('api/update/<int:pk>/', views.firearm_update,  name='api_update'),
    path('api/delete/<int:pk>/', views.firearm_delete,  name='api_delete'),
    
    # PAR Records
    path('par/',                 views.par_management,  name='par_index'),
    path('par/print/<int:pk>/',  views.print_par,       name='print_par'),
    path('par/edit/<int:pk>/',   views.edit_par,        name='edit_par'),
    path('par/delete/<int:pk>/', views.delete_par,      name='delete_par'),
    path('api/par/list/',        views.api_par_list,    name='api_par_list'),

    path('activity-logs/', views.firearms_activitylog, name='activity_logs'),
    path('activity-logs/api/', views.firearms_activitylog_api, name='activity_logs_api'),
]