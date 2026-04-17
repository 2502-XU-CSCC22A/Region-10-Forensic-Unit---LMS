from django.shortcuts import render
from .models import DisposalItem

# Create your views here.
def disposal_list(request):
    return render(request, 'disposal/disposal.html')

def disposal_view(request):
    # This line queries your Supabase Postgres database
    all_items = DisposalItem.objects.all() 
    
    return render(request, 'disposal/disposal.html', {'items': all_items})