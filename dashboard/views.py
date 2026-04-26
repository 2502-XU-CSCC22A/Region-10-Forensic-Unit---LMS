from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from config.models import Asset, AssetStatus, Category
from disposal.models import DisposalItem


@login_required
def dashboard_view(request):
    """
    Dashboard home page.
    Queries Asset by Category for stat cards and the activity feed.
    Cards: Total Assets, Total Firearms, Total Mobility,
           Total Communication Devices, Total Investigative Equipment, Total BER Items
    """

    def count_category(name):
        """Count assets whose category_name matches (case-insensitive)."""
        return Asset.objects.filter(
            category__category_name__iexact=name
        ).count()

    def count_status(name):
        """Count assets whose status_name matches (case-insensitive)."""
        return Asset.objects.filter(
            status__status_name__iexact=name
        ).count()

    total_assets         = Asset.objects.count()
    total_firearms       = count_category('Firearms')
    total_mobility       = count_category('Mobility')
    total_communications = count_category('Communications')
    total_investigative  = count_category('Investigative Equipment')
    total_ber            = count_status('BER')

    # Activity feed — 10 most recently added assets
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
            'item':      f'{asset.category.category_name} ID {asset.property_no}',
            'change':    asset.status.status_name if asset.status else '—',
            'timestamp': asset.date_acquired.strftime('%b %d, %Y'),
            'unread':    True,
        })

    context = {
        'total_assets':         total_assets,
        'total_firearms':       total_firearms,
        'total_mobility':       total_mobility,
        'total_communications': total_communications,
        'total_investigative':  total_investigative,
        'total_ber':            total_ber,
        'activities':           activities,
        'notification_count':   min(len(activities), 99),
    }
    return render(request, 'dashboard/dashboard.html', context)
