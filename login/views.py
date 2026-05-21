from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login

from .models import LoginToken

# Create your views here.
def login(request):
    return render(request, 'login/login.html')

def password_complete_view(request):
    return render(request, 'login/password_reset_complete.html')

def password_confirm_view(request):
    return render(request, 'login/password_reset_confirm.html')

def password_done_view(request):
    return render(request, 'login/password_reset_done.html')

def password_form_view(request):
    return render(request, 'login/password_reset_form.html')

# ── Login ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard_view')

    if request.method == 'POST':
        uname    = request.POST.get('username', '').strip()
        passw    = request.POST.get('password', '')
        remember = request.POST.get('remember')

        user = authenticate(request, username=uname, password=passw)

        if user is not None:
            token = LoginToken.generate(user)
            # Carry the "remember me" preference through the token step
            request.session['_pending_remember'] = bool(remember)
            return redirect('verify_token', token=token)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'Login/login.html')


def verify_token_view(request, token):
    
    user = LoginToken.consume(token)

    if user is None:
        messages.error(
            request,
            'This login link has expired or is invalid. Please log in again.'
        )
        return redirect('login')

    remember = request.session.pop('_pending_remember', False)
    auth_login(request, user)

    if remember:
        request.session.set_expiry(1_209_600)   
    else:
        request.session.set_expiry(0)          

    return redirect('dashboard:dashboard_view')


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    from django.contrib.auth.models import User

    # ── Stats ─────────────────────────────────────────────────────────────────
    return render(request, 'dashboard/dashboard.html')


# ── Logout ────────────────────────────────────────────────────────────────────

def logout_view(request):
    logout(request)
    return redirect('login')