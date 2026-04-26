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
    """
    Step 1 – Verify username/password against the database.
    On success, issue a one-time DB-backed token and redirect to the
    verify step.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

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
    """
    Step 2 – Validate and consume the one-time token in the URL.
    Visiting this URL destroys the token; it cannot be reused.
    """
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
        request.session.set_expiry(1_209_600)   # 2 weeks
    else:
        request.session.set_expiry(0)            # expires on browser close

    return redirect('dashboard')


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    """
    Main dashboard.  Passes summary statistics and activity feed to the
    template so the numbers in the stat cards are real.
    """
    from django.contrib.auth.models import User

    # ── Stats ─────────────────────────────────────────────────────────────────
    # These are placeholders — wire them to your real models once you have them.
    context = {
        'total_assets'    : 160,
        'issued_items'    : 67,
        'available_items' : 88,
        'low_stock'       : 5,
        'ber_items'       : 160,
        'disposal_items'  : 160,

        # Activity feed — replace with QuerySet from your Asset / AuditLog model
        'activities': [
            {
                'initials'  : 'JA',
                'actor'     : 'Logistics Officer',
                'action'    : 'removed',
                'item'      : 'firearm ID 204',
                'timestamp' : '11 seconds ago',
                'unread'    : True,
            },
            {
                'initials'  : 'JA',
                'actor'     : 'Logistics Officer',
                'action'    : 'issued a new',
                'item'      : 'vehicle ID VE001',
                'timestamp' : '52 seconds ago',
                'unread'    : True,
            },
            {
                'initials'  : 'JA',
                'actor'     : 'Logistics Officer',
                'action'    : 'logged in',
                'item'      : '',
                'timestamp' : '1 minute ago',
                'unread'    : True,
            },
            {
                'initials'  : 'JA',
                'actor'     : 'Logistics Officer',
                'action'    : 'edited',
                'item'      : 'firearm ID 067',
                'timestamp' : '01/24/2026',
                'change'    : 'Model: Boobie → Model: A$$',
                'unread'    : True,
            },
        ],

        'notification_count': 9,
        'user': request.user,
    }
    return render(request, 'Dashboard/dashboard.html', context)


# ── Logout ────────────────────────────────────────────────────────────────────

def logout_view(request):
    logout(request)
    return redirect('login')