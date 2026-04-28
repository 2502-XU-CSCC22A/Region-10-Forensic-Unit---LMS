from django.shortcuts import render, redirect
from django.utils import timezone
import uuid
from mobility.views import Vehicle
from .models import Communication
from config.models import Category, Asset  # Replace 'config' with the folder where Asset lives

# VIEW 1: Displays the table (Keep this!)
def communications_list(request):
    # Fetch all records from Supabase to show in the table
    items = Communication.objects.all() 
    return render(request, 'communications/communications.html', {'items': items})
