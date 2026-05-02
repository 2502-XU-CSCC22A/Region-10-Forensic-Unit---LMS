from django.shortcuts import render, redirect
from .models import Communication, CommunicationPARRecord
from .forms import CommunicationPARForm
from django.utils import timezone
import uuid

# 1. FIX IMPORTS: Point these to your project's folder names
from .models import Communication
from config.models import Category, Asset  # Replace 'config' with the folder where Asset lives

# VIEW 1: Displays the table (Keep this!)
def communications_list(request):
    # Fetch all records from Supabase to show in the table
    items = Communication.objects.all() 
    return render(request, 'communications.html', {'items': items})

def par_monitoring(request):
    return render(request, 'par_monitoring.html')

def activity_logs(request):
    return render(request, 'activity_logs.html')

def par_monitoring(request):
    pars = CommunicationPARRecord.objects.select_related("communication").all().order_by("-created_at")

    if request.method == "POST":
        p_form = CommunicationPARForm(request.POST)
        if p_form.is_valid():
            p_form.save()
            return redirect("par_monitoring")
    else:
        p_form = CommunicationPARForm()

    return render(request, "par_monitoring.html", {
        "p_form": p_form,
        "pars": pars,
    })
def print_par(request, pk):
    par = CommunicationPARRecord.objects.select_related("communication").get(pk=pk)

    return render(request, "print_par.html", {
        "par": par
    })