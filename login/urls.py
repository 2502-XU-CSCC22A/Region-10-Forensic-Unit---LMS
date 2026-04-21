from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login/'),
    path('reset/complete/', views.password_complete_view, name='password_reset_complete'),
    path('reset/confirm/<uidb64>/<token>/', views.password_confirm_view, name='password_reset_confirm'),
    path('reset/done/', views.password_done_view, name='password_reset_done'),
    path('reset/', views.password_form_view, name='password_reset_form'),
]