# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from .views import home_view
from login.views import login_view, verify_token_view, dashboard_view, logout_view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    path('disposal/', include('disposal.urls')),
    path('login/', include ('login.urls')),
    path('', home_view, name='home'), 
    path('mobility/', include('mobility.urls')), # Dashboard will be at /mobility/

    # Home / Landing page
    path('', TemplateView.as_view(template_name='Home/home.html'), name='home'),

    # ── Authentication ────────────────────────────────────────────────────────
    # Step 1: submit credentials → token issued
    path('login/', login_view, name='login'),
    # Step 2: token in URL is consumed → session created
    path('login/verify/<str:token>/', verify_token_view, name='verify_token'),
    # Logout
    path('logout/', logout_view, name='logout'),

    # ── Dashboard ─────────────────────────────────────────────────────────────
    path('dashboard/', dashboard_view, name='dashboard'),

    # ── Password Reset (Django built-ins) ─────────────────────────────────────
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/reset-password/done/',
    ), name='reset_password'),

    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html',
    ), name='password_reset_done'),

    path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset-password/complete/',
    ), name='password_reset_confirm'),

    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html',
    ), name='password_reset_complete'),
]
