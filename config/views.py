from django.shortcuts import render
from django.contrib.auth import login as auth_login

def home_view(request):
    return render(request, 'home.html')
