# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('disposal/', include('disposal.urls')),
    path('login/', include ('login.urls')),
    path('', home_view, name='home'), 
    
]
=======
    path('mobility/', include('mobility.urls')), # Dashboard will be at /mobility/
]
>>>>>>> origin/mobility
