from django.shortcuts import render, redirect
from django.utils import timezone
import uuid
from mobility.views import Vehicle
from .models import Communication
from config.models import Category, Asset  


def communications_list(request):

    items = Communication.objects.all() 
    return render(request, 'communications/communications.html', {'items': items})

def par_monitoring(request):
    return render(request, 'par_monitoring.html')

def activity_logs(request):
    return render(request, 'communications/activity_logs.html')