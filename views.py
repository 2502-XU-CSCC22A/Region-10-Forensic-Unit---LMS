from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from config.models import Asset, AssetStatus, Category


@login_required
def dashboard_view(request):
    """
    Main dashboard home page.

    Passes summary counts to the template so the cards can be populated
    without extra JavaScript calls.
    """
    context = {
        'total_assets':      Asset.objects.count(),
        'total_categories':  Category.objects.count(),
        'status_counts':     {
            s.status_name: Asset.objects.filter(status=s).count()
            for s in AssetStatus.objects.all()
        },
    }
    return render(request, 'Dashboard/dashboard.html', context)
