from django.shortcuts import render

# Create your views here.
def disposal_list(request):
    return render(request, 'disposal/disposal.html')