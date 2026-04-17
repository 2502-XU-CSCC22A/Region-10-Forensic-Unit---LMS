from django.urls import path
from . import views

urlpatterns = [
    path('', views.disposal_list, name='disposal_list'),
]