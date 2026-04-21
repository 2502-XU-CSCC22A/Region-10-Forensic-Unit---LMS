from django.urls import path
from . import views

urlpatterns = [
    # When someone visits /disposal/, call the disposal_list view
    path('', views.disposal_list, name='disposal_list'),
    path('disposal/export/', views.export_disposal_csv, name='export_disposal_csv'),
]