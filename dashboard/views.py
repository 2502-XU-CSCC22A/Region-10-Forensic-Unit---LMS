from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType

from config.models import Asset, AssetStatus, Category
from firearms.models import Firearm
from communications.models import Communication
from mobility.models import Vehicle
from InvestigativeEquipment.models import InvestigativeDetails
from disposal.models import DisposalItem

def _role_label(user):
    try:
        return user.userprofile.role 
    except:
        return 'Staff'

@login_required
def dashboard_view(request):
    def count_category(name):
        return Asset.objects.filter(category__category_name__iexact=name).count()

    def count_status(name):
        return Asset.objects.filter(status__status_name__iexact=name).count()

    total_assets         = Asset.objects.exclude(status_id__in=[4, 5]).count()
    total_firearms       = Firearm.objects.count()
    total_mobility       = Vehicle.objects.count()
    total_communications = Communication.objects.exclude(status_id__in=[4, 5]).count()
    total_investigative  = InvestigativeDetails.objects.count()
    total_ber = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
    ).count()
    
    users = User.objects.filter(is_active=True).order_by('-last_login')[:50]
    asset_ct = ContentType.objects.get_for_model(Asset)
        
    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None

    raw_logs = LogEntry.objects.filter(content_type=asset_ct).select_related('user').order_by('-action_time')[:30]
    
    ACTION_FLAG_MAP = {
        ADDITION:  'added asset',
        CHANGE:    'updated asset',
        DELETION:  'removed asset',
    }

    read_ids = set(request.session.get('read_activity_ids', []))

    activities = []

    if raw_logs.exists():
        for entry in raw_logs:
            u = entry.user
            role  = _role_label(u)
            name  = u.get_full_name() or u.username
            actor = f'{name} ({role})'

            action_text = ACTION_FLAG_MAP.get(entry.action_flag, 'modified asset')
            initials    = ''.join(p[0].upper() for p in name.split()[:2]) or u.username[0].upper()

            activities.append({
                'id':        entry.id,
                'initials':  initials,
                'actor':     actor,
                'action':    action_text,
                'item':      entry.object_repr,
                'timestamp': entry.action_time.strftime('%b %d, %Y %I:%M %p'),
                'unread':    entry.id not in read_ids,
            })
    else:
        recent_assets = (
            Asset.objects
            .select_related('status', 'category')
            .order_by('-id')[:5]
        )
        ACTION_TYPES = [
            ('recorded asset', 'added'),
            ('updated asset',  'modified'),
            ('removed asset',  'removed'),
            ('logged in',      'login'),
        ]
        for i, asset in enumerate(recent_assets):
            initials    = ''.join(w[0].upper() for w in asset.model.split()[:2]) or 'A'
            action_label, action_type = ACTION_TYPES[i % len(ACTION_TYPES)]

            if action_type == 'login':
                action_text = 'logged in'
                item_text   = ''
            elif action_type == 'removed':
                action_text = f'removed asset ID {asset.property_no}'
                item_text   = ''
            else:
                action_text = action_label
                item_text   = f'{asset.category.category_name} – {asset.property_no}'

            activities.append({
                'id':        asset.id,
                'initials':  initials,
                'actor':     'Logistics Officer (Logistics)',
                'action':    action_text,
                'item':      item_text,
                'timestamp': asset.date_acquired.strftime('%b %d, %Y'),
                'unread':    asset.id not in read_ids,
            })

    unread_count = sum(1 for a in activities if a['unread'])

    context = {
        'total_assets':         total_assets,
        'total_firearms':       total_firearms,
        'total_mobility':       total_mobility,
        'total_communications': total_communications,
        'total_investigative':  total_investigative,
        'total_ber':            total_ber,
        'activities':           activities,
        'notification_count':   unread_count,
        'current_user_role': current_user_role,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
@require_POST
def mark_all_read(request):
    """AJAX endpoint — marks all current activity items as read in the session."""
    from django.contrib.contenttypes.models import ContentType
    asset_ct   = ContentType.objects.get_for_model(Asset)
    recent_ids = list(
        LogEntry.objects
        .filter(content_type=asset_ct)
        .order_by('-action_time')
        .values_list('id', flat=True)[:5]
    )
    if not recent_ids:
        recent_ids = list(Asset.objects.order_by('-id').values_list('id', flat=True)[:5])

    existing = set(request.session.get('read_activity_ids', []))
    existing.update(recent_ids)
    request.session['read_activity_ids'] = list(existing)
    request.session.modified = True
    return JsonResponse({'status': 'ok', 'read_count': len(recent_ids)})

