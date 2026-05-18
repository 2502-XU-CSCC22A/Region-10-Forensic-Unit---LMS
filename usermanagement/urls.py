from django.urls import path
from .views import user_list, update_user_role, update_user
from login.views import logout_view

app_name = "user_management"

urlpatterns = [
    path('', user_list, name='user_list'),
    path('update-role/<int:user_id>/', update_user_role, name='update_user_role'),
    path('update-user/<int:user_id>/', update_user, name='update_user'),
    path('logout/', logout_view, name='logout'),
]