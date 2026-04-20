from datetime import date
from django.shortcuts import render
from django.http import JsonResponse
from .models import DisposalItem

# Create your views here.
def disposal_list(request):
    # This fetches all records from the Supabase table
    items = DisposalItem.objects.all() 
    return render(request, 'disposal/disposal.html', {'items': items})
