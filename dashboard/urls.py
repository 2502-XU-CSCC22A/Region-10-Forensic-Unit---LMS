from django.urls import path
from login.views import logout_view
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard_view'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('api/recent-activities/', views.recent_activities_api, name='recent_activities_api'),
    path('api/assets-log/', views.asset_activities_api, name='asset_activities_api'),
    path('api/notifications-log/', views.notifications_api, name='notifications_api'),
    path('logout/', logout_view, name='logout'),
]