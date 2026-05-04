from django.urls import path
from login.views import logout_view
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard_view'),
    path('logout/', logout_view, name='logout'),
]