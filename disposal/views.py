from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q, Count
from mobility.models import Vehicle
from config.models import Asset, AssetStatus, Personnel
from .models import DisposalItem, DisposalActivityLog
from django.core.paginator import Paginator

def export_disposal_csv(request):
    items = DisposalItem.objects.select_related('asset_ptr', 'asset_ptr__category').all()
    
    device_type = request.GET.get('device_type')
    if device_type and device_type != 'all':
        items = items.filter(asset_ptr__category__category_name__iexact=device_type)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="disposal_report_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Asset Model', 'Serial Number', 'Category', 'Expiry Date', 'Reason'])

    for item in items:
        writer.writerow([
            item.asset_ptr.model,
            item.asset_ptr.serial_no,
            item.asset_ptr.category.category_name,
            item.disposal_reason
        ])

    return response

from django.shortcuts import render, redirect
from .models import Asset, DisposalItem
from config.models import Personnel  # Ensure this import is correct

def disposal_list(request):
    all_items = DisposalItem.objects.filter(status_id = 4).order_by('-disposal_date')
    
    paginator = Paginator(all_items, 15)
    page_number = request.GET.get('page')
    disposal_items = paginator.get_page(page_number)
    
    logs = DisposalActivityLog.objects.all().order_by('-timestamp')
    
    last_item = DisposalItem.objects.order_by('-last_sync').first()
    sync_time = last_item.last_sync if last_item else None
    
    today = timezone.now().date()
  
    ber_today_count = DisposalItem.objects.filter(
        disposal_date__date=today
    ).count()
    
    comms_ber = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
        asset_ptr__category__category_name='communications'
    ).count()
    
    mobility_ber = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
        asset_ptr__category__category_name='mobility'
    ).count()
    
    firearms_ber = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
        asset_ptr__category__category_name='firearms'
    ).count()
    
    inves_ber = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
        asset_ptr__category__category_name='investigative_equipment'
    ).count()
    
    total_ber = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
    ).count()
    
    if request.method == "POST":
        asset_id = request.POST.get('asset_id')
        reason = request.POST.get('reason')
        personnel_id = request.POST.get('personnel_id') 
        
        asset = Asset.objects.get(id=asset_id)
        personnel = Personnel.objects.get(PersonnelID=personnel_id)

        DisposalItem.objects.create(
            asset_ptr=asset,
            processed_by=personnel, 
            disposal_reason=reason,
        )
        return redirect('disposal_list')

    return render(request, 'disposal/disposal.html', {
        'logs': logs,
        'last_sync_time': sync_time,
        'ber_today_count': ber_today_count,
        'current_time': timezone.now(),
        'comms_ber': comms_ber,
        'firearms_ber': firearms_ber,
        'mobility_ber': mobility_ber,
        'inves_ber': inves_ber,
        'total_ber': total_ber,
        'disposal_items': disposal_items
    })

def disposal_list_supervisor(request):
    items = Asset.objects.filter(status_id = 4)

    return render(request, 'disposal/disposal_supervisor.html', {'items': items})

# --- ACTIVITY LOG ---
def history_log(request):
    logs = DisposalActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'disposal/history.html', {'items': logs})

def finalize_removal(request, pk):
    disposal_entry = DisposalItem.objects.filter(pk=pk).first()
    
    if disposal_entry:
        asset = disposal_entry.asset_ptr
        reason = disposal_entry.disposal_reason
    else:
        asset = get_object_or_404(Asset, pk=pk)
        reason = "Marked for Disposal via Status Update"

    disposed_status = get_object_or_404(AssetStatus, status_id=5) 
    asset.status_id = disposed_status
    asset.save()

    DisposalActivityLog.objects.create(
        user=request.user,
        asset=asset,
        action_type='REMOVE',
        disposal_reason=reason,
        description=f"Finalized disposal for {asset.model} ({asset.serial_no})"
    )

    if disposal_entry:
        disposal_entry.delete()

    messages.success(request, f"Asset {asset.serial_no} successfully disposed.")
    return redirect('disposal:history_log')