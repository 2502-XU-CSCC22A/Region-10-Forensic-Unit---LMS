from django.urls import path
from . import views

app_name= 'communications'

urlpatterns = [
    path('', views.communications_list, name='communications_list'),
    
]