from django.urls import path
from login.views import logout_view
from . import views

app_name= 'disposal'

urlpatterns = [
    path('', views.disposal_list, name='disposal_list'),
    path('history/', views.history_log, name='history_log'),
    path('disposal/export/', views.export_disposal_csv, name='export_disposal_csv'),
    path('remove-item/<int:pk>/', views.finalize_removal, name='finalize_removal'),
    path('logout/', logout_view, name='logout'),
]