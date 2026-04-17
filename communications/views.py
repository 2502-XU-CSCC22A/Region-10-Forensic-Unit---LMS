from django.shortcuts import render
from .models import Communication

# This view will handle your main communications dashboard
def communications_list(request):
    """
    Fetches all communication items from the Supabase Postgres database
    and renders them using the communications.html template.
    """
    # Fetching the data from your Communication model
    all_items = Communication.objects.all() 
    
    # Rendering 'communications.html' which lives in templates-comms
    return render(request, 'communications.html', {'items': all_items})

def home_view(request):
    """
    Renders the generic landing page.
    """
    return render(request, 'home.html')