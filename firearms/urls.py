# firearms/urls.py
# Wire this into config/urls.py with:
#   path('firearms/', include('firearms.urls', namespace='firearms')),

from django.urls import path
from . import views

app_name = 'firearms'

urlpatterns = [
    path('', views.index, name='index'),
]