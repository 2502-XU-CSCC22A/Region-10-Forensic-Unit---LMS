from django.shortcuts import render

from config.models import Asset, AssetStatus
from django.db.models import Q
from mobility.models import Vehicle
from disposal.models import DisposalItem
from firearms.models import Firearm
from communications.models import Communication

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
        .order_by('-id')[:10]
    )

    activities = []
    for asset in recent_assets:
        initials = ''.join(w[0].upper() for w in asset.model.split()[:2]) or 'A'
        activities.append({
            'initials':  initials,
            'actor':     'Logistics Officer',
            'action':    'recorded asset',
            'item':      f'{asset.category.category_name} – {asset.property_no}',
            'change':    asset.status.status_name if asset.status else '—',
            'timestamp': asset.date_acquired.strftime('%b %d, %Y'),
            'unread':    True,
        })

    context = {
        'vehicles':           all_v.filter(query),
        'total_vehicles':     all_v.count(),
        'total_assets':       all_a.count(),
        'total_disposal':     all_d.count(),
        'total_firearms':     all_f.count(),
        'total_comms':        all_c.count(),
        # 'total_inves':        all_i.count(),
        'activities':         activities,
        'notification_count': min(len(activities), 99),
    }

    return render(request, 'dashboard/dashboard.html', context)