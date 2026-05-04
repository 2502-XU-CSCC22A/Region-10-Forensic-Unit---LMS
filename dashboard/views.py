from django.shortcuts import render
from config.models import Asset, AssetStatus
from django.db.models import Q
from mobility.models import Vehicle
from disposal.models import DisposalItem
from firearms.models import Firearm
from communications.models import Communication
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

@login_required
def dashboard_view(request):
    query = Q()
    plate_no = request.GET.get('plate_no')
    if plate_no:
        query &= Q(plate_number__icontains=plate_no) | Q(conduction_number__icontains=plate_no)

    all_v = Vehicle.objects.all()
    all_a = Asset.objects.exclude(status_id__in=[5])
    all_d = DisposalItem.objects.all()
    all_f = Firearm.objects.all()
    all_c = Communication.objects.exclude(status_id__in=[4, 5])

    recent_assets = (
        Asset.objects
        .select_related('status', 'category')
        .order_by('-id')[:5]
    )

    ACTION_TYPES = [
        ('recorded asset',  'added'),
        ('updated asset',   'modified'),
        ('removed asset',   'removed'),
        ('logged in',       'login'),
    ]
    
    read_ids = set(request.session.get('read_activity_ids', []))

    activities = []
    for i, asset in enumerate(recent_assets):
        initials = ''.join(w[0].upper() for w in asset.model.split()[:2]) or 'A'
        action_label, action_type = ACTION_TYPES[i % len(ACTION_TYPES)]

        if action_type == 'login':
            action_text  = 'logged in'
            item_text    = ''
        elif action_type == 'removed':
            action_text  = f'removed asset ID {asset.property_no}'
            item_text    = ''
        else:
            action_text  = action_label
            item_text    = f'{asset.category.category_name} – {asset.property_no}'

        activities.append({
            'id':          asset.id,
            'initials':    initials,
            'actor':       'Logistics Officer',
            'action':      action_text,
            'item':        item_text,
            'change':      asset.status.status_name if asset.status else '—',
            'timestamp':   asset.date_acquired.strftime('%b %d, %Y'),
            'unread':      asset.id not in read_ids,
            'action_type': action_type,
        })
        
        unread_count = sum(1 for a in activities if a['unread'])

    context = {
        'vehicles':           all_v.filter(query),
        'total_vehicles':     all_v.count(),
        'total_assets':       all_a.count(),
        'total_disposal':     all_d.count(),
        'total_firearms':     all_f.count(),
        'total_comms':        all_c.count(),
        # 'total_inves':        all_i.count(),
        'activities':           activities,
        'notification_count':   min(len(activities), 99),
    }
    
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
@require_POST
def mark_all_read(request):
    """AJAX endpoint — marks all current activity items as read in the session."""
    recent_ids = list(
        Asset.objects.order_by('-id').values_list('id', flat=True)[:5]
    )
    existing = set(request.session.get('read_activity_ids', []))
    existing.update(recent_ids)
    request.session['read_activity_ids'] = list(existing)
    request.session.modified = True
    return JsonResponse({'status': 'ok', 'read_count': len(recent_ids)})