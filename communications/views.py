from django.shortcuts import render, redirect
from django.utils import timezone
import uuid
from mobility.views import Vehicle
from firearms.models import Firearm
from disposal.models import DisposalItem
from .models import Communication
from config.models import Category, Asset, AssetStatus


def communications_list(request):

    items = Communication.objects.all() 
    
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.all()
    
    return render(request, 'communications/communications.html', {
        'items': items,
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count()
        })

def par_monitoring(request):
    return render(request, 'par_monitoring.html')

def activity_logs(request):
    return render(request, 'communications/activity_logs.html')