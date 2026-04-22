from django.shortcuts import render

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