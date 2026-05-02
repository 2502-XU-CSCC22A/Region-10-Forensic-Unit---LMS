from django.urls import path
from . import views

app_name= 'communications'

urlpatterns = [
    path('', views.communications_list, name='communications_list'),
    path('par/print/<int:pk>/', views.print_par, name='print_par'),
    path('par/', views.par_monitoring, name='par_monitoring'),
    path('reports/', views.activity_logs, name='activity_logs'),
]