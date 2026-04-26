from django.urls import path
from . import views

app_name= 'disposal'

urlpatterns = [
    # When someone visits /disposal/, call the disposal_list view
    path('', views.disposal_list, name='disposal_list'),
    path('history/', views.history_log, name='history_log'),
    path('disposal/export/', views.export_disposal_csv, name='export_disposal_csv'),
    path('remove-item/<int:pk>/', views.finalize_removal, name='finalize_removal'),
]