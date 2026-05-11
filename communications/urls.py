from django.urls import path
from login.views import logout_view
from . import views

app_name= 'communications'

urlpatterns = [
    path("", views.communications_list, name="communications_list"),
    path("par/print/<int:pk>/", views.print_par, name="print_par"),
    path("par/edit/<int:pk>/", views.edit_par, name="edit_par"),
    path("par/delete/<int:pk>/", views.delete_par, name="delete_par"),
    path("par/", views.par_monitoring, name="par_monitoring"),
    path("ics/print/<int:pk>/", views.print_ics, name="print_ics"),
    path("ics/edit/<int:pk>/", views.edit_ics, name="edit_ics"),
    path("ics/delete/<int:pk>/", views.delete_ics, name="delete_ics"),
    path("ics/", views.ics_monitoring, name="ics_monitoring"),
    path("reports/", views.activity_logs, name="activity_logs"),
    path('logout/', logout_view, name='logout'),
]
