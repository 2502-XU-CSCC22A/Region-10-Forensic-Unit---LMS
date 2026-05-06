import json
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from mobility.models import Vehicle
from disposal.models import DisposalItem
from communications.models import Communication
from firearms.models import Firearm

@login_required
def user_list(request):
    users = User.objects.select_related('userprofile') \
        .filter(is_active=True) \
        .order_by('-last_login')[:50]
        
    vehicle_all = Vehicle.objects.count()
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearm_all = Firearm.objects.exclude(status_id__in=[4, 5]).count()
    disposal_all = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
    ).count()

    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None

    return render(request, 'usermanagement/usermanagement.html', {
        'users': users,
        'vehicle_all': vehicle_all,
        'comms_all': comms_all,
        'disposal_all': disposal_all,
        'firearm_all': firearm_all,
        'current_user_role': current_user_role,
    })


@login_required
@require_POST
def update_user_role(request, user_id):
    if request.user.userprofile.role != 'Admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        new_role = data.get('role')

        if new_role not in ['User', 'Admin']:
            return JsonResponse({'success': False, 'error': 'Invalid role'}, status=400)

        target_user = User.objects.get(id=user_id)
        target_user.userprofile.role = new_role
        target_user.userprofile.save()

        return JsonResponse({'success': True})
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)