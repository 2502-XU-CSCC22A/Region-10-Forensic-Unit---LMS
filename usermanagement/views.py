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
from InvestigativeEquipment.models import InvestigativeDetails
from firearms.models import Firearm

@login_required
def user_list(request):
    users = User.objects.select_related('userprofile') \
        .filter(is_active=True) \
        .order_by('-last_login')[:50]
        
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearm_all = Firearm.objects.exclude(status_id__in=[4, 5]).count()
    disposal_all = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
    ).count()
    inves_all = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5]).count()

    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None

    return render(request, 'usermanagement/usermanagement.html', {
        'users': users,
        'vehicle_all': visible_v.count(),
        'comms_all': comms_all,
        'disposal_all': disposal_all,
        'firearm_all': firearm_all,
        'current_user_role': current_user_role,
        'inves_all': inves_all,
    })


@login_required
@require_POST
def update_user_role(request, user_id):
    if request.user.userprofile.role != 'Admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        new_role = data.get('role')

        if new_role not in ['Supervisor', 'Admin']:
            return JsonResponse({'success': False, 'error': 'Invalid role'}, status=400)

        target_user = User.objects.get(id=user_id)
        target_user.userprofile.role = new_role
        target_user.userprofile.save()

        return JsonResponse({'success': True})
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def update_user(request, user_id):
    if request.user.userprofile.role != 'Admin':
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    try:
        data = json.loads(request.body)
        first_name = data.get('first_name', '').strip()
        last_name  = data.get('last_name', '').strip()
        email      = data.get('email', '').strip()

        # ── Server-side validation ────────────────────────────────────────
        if not first_name:
            return JsonResponse({'success': False, 'error': 'First name is required.'}, status=400)
        if len(first_name) > 150:
            return JsonResponse({'success': False, 'error': 'First name must be 150 characters or fewer.'}, status=400)
        if len(last_name) > 150:
            return JsonResponse({'success': False, 'error': 'Last name must be 150 characters or fewer.'}, status=400)
        if not email:
            return JsonResponse({'success': False, 'error': 'Email is required.'}, status=400)
        if len(email) > 254:
            return JsonResponse({'success': False, 'error': 'Email must be 254 characters or fewer.'}, status=400)

        target_user = User.objects.get(id=user_id)

        # ── Check email uniqueness (exclude the user being edited) ────────
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            return JsonResponse({'success': False, 'error': 'This email is already in use.'}, status=409)

        target_user.first_name = first_name
        target_user.last_name  = last_name
        target_user.email      = email
        target_user.save()

        return JsonResponse({'success': True})

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)