from django.shortcuts import render
from django.http import JsonResponse
from .models import BerItem
from .models import DisposalItem

# Create your views here.
def disposal_list(request):
    return render(request, 'disposal/disposal.html')

def disposal_view(request):
    # This line queries your Supabase Postgres database
    all_items = DisposalItem.objects.all() 
    
    return render(request, 'disposal/disposal.html', {'items': all_items})

def ber_items_api(request):
    data = list(BerItem.objects.values('title', 'description', 'category', 'image_url'))
    return JsonResponse(data, safe=False)