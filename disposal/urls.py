from django.urls import path
from . import views

urlpatterns = [
    path('', views.disposal_list, name='disposal_list'),
    path('api/ber-items/', views.ber_items_api, name='ber_items_api'),
]