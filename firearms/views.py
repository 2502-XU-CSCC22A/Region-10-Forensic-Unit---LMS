
from django.shortcuts import render


def index(request):
   
    return render(request, 'firearms/firearms_main.html', {
        'active_page': 'firearms',
    })