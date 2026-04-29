from django.urls import path
from .views import user_list

app_name = "user_management"

urlpatterns = [
    path('', user_list, name='user_list'),
]