from django.shortcuts import render, redirect
from .models import Communication, CommunicationPARRecord
from .forms import CommunicationPARForm
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
    return render(request, 'communications/par_monitoring.html')

def activity_logs(request):
    return render(request, 'communications/activity_logs.html')

def par_monitoring(request):
    pars = CommunicationPARRecord.objects.select_related("communication").all().order_by("-created_at")
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.all()
    
    if request.method == "POST":
        p_form = CommunicationPARForm(request.POST)
        if p_form.is_valid():
            p_form.save()
            return redirect("par_monitoring")
    else:
        p_form = CommunicationPARForm()

    return render(request, "communications/par_monitoring.html", {
        "p_form": p_form,
        "pars": pars,
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count()
    })
def print_par(request, pk):
    par = CommunicationPARRecord.objects.select_related("communication").get(pk=pk)

    return render(request, "communications/print_par.html", {
        "par": par
    })