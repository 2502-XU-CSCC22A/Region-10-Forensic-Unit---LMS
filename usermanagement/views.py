from django.shortcuts import render
from .models import UserProfile

def user_list(request):
    users = UserProfile.objects.all()
    return render(request, 'usermanagement/usermanagement.html', {
        'users': users
    })