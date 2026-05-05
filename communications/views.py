from django.shortcuts import render, redirect
from .models import Communication, CommunicationPARRecord
from django.contrib.auth.models import User
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
    
    users = User.objects.select_related('userprofile') \
        .filter(is_active=True) \
        .order_by('-last_login')[:50]
        
    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None
    
    return render(request, 'communications/communications.html', {
        'items': items,
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count(),
        'current_user_role':  current_user_role
        })

def par_monitoring(request):
    return render(request, 'communications/par_monitoring.html')

def activity_logs(request):
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    all_d = DisposalItem.objects.all()
    
    users = User.objects.select_related('userprofile') \
        .filter(is_active=True) \
        .order_by('-last_login')[:50]
        
    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None
    
    return render(request, 'communications/activity_logs.html', {
        'total_comms': all_c.count() ,
        'total_ber': all_d.count(),
        'total_vehicles': all_v.count(),
        'total_firearms': all_f.count(),
        'current_user_role':  current_user_role
    })

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