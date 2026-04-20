from django.urls import path
from . import views

urlpatterns = [
    # When someone visits /disposal/, call the disposal_list view
    path('', views.disposal_list, name='disposal_list'),
]