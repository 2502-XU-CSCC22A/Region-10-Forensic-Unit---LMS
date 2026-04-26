from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from config.models import Asset, AssetStatus

@login_required
def dashboard_view(request):

    def count_status(name):
        return Asset.objects.filter(
            status__status_name__iexact=name
        ).count()

    total_assets    = Asset.objects.count()
    issued_items    = count_status('Issued')
    available_items = count_status('Serviceable')
    low_stock       = count_status('Low Stock')
    ber_items       = count_status('BER')
    disposal_items  = count_status('For Disposal')

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
            'actor':     asset.property_no,
            'action':    'recorded asset',
            'item':      asset.model,
            'change':    asset.status.status_name if asset.status else '—',
            'timestamp': asset.date_acquired.strftime('%b %d, %Y'),
            'unread':    False,
        })

    context = {
        'total_assets':       total_assets,
        'issued_items':       issued_items,
        'available_items':    available_items,
        'low_stock':          low_stock,
        'ber_items':          ber_items,
        'disposal_items':     disposal_items,
        'activities':         activities,
        'notification_count': min(total_assets, 99),
    }
    return render(request, 'Dashboard/dashboard.html', context)