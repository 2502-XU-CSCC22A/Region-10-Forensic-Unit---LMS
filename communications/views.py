from django.shortcuts import render, redirect
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
