from django.urls import path
from django.contrib.auth import views as auth_views  # Missing this for password resets
from . import views  # This imports your views.py file

urlpatterns = [
    # ── Authentication ────────────────────────────────────────────────────────
    # Notice we now use views.login_view because you imported 'views'
    path('login/', views.login_view, name='login'),
    path('login/verify/<str:token>/', views.verify_token_view, name='verify_token'),
    path('logout/', views.logout_view, name='logout'),

    # ── Dashboard ─────────────────────────────────────────────────────────────
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # ── Password Reset (Now auth_views is defined) ────────────────────────────
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