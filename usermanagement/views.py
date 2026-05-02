from django.contrib.auth.models import User
from django.shortcuts import render
from .models import UserProfile
from mobility.models import Vehicle
from disposal.models import DisposalItem
from communications.models import Communication
from firearms.models import Firearm

def user_list(request):
    users = User.objects.select_related('userprofile') \
        .filter(is_active=True) \
        .order_by('-last_login')[:50]
        
    vehicle_all = Vehicle.objects.count()
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    disposal_all = DisposalItem.objects.count()
    firearm_all = Firearm.objects.exclude(status_id__in=[4, 5]).count()

    return render(request, 'usermanagement/usermanagement.html', {
        'users': users,
        'vehicle_all': vehicle_all,
        'comms_all': comms_all,
        'disposal_all': disposal_all,
        'firearm_all': firearm_all,
    })