from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

def usermanagement(request):
    return render(request, 'usermanagement/usermanagement.html')