from django.urls import path
from . import views
 
app_name = 'firearms'
 
urlpatterns = [
    path('',                     views.index,           name='index'),
    path('api/list/',            views.firearm_list,    name='api_list'),
    path('api/create/',          views.firearm_create,  name='api_create'),
    path('api/update/<int:pk>/', views.firearm_update,  name='api_update'),
    path('api/delete/<int:pk>/', views.firearm_delete,  name='api_delete'),
]
 