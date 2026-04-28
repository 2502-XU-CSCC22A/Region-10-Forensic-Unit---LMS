from django.shortcuts import render
from usermanagement.models import UserProfile

def usermanagement(request):
    users = UserProfile.objects.all()
    return render(request, 'usermanagement/usermanagement.html', {'users': users})