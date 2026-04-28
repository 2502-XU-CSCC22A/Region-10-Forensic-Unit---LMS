from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse
from django.db.models import Q
from mobility.models import Vehicle
from config.models import Asset, AssetStatus
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import DisposalItem, DisposalActivityLog

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
            item.expiry_date,
            item.disposal_reason
        ])

    return response

def disposal_list(request):
    # 1. Get Assets explicitly marked as 'BER' (Assuming ID 4 is BER)
    # This acts as your 'Automatic' list
    items = Asset.objects.filter(status_id = 4)

    # 2. Get items already in the DisposalItem table (Manual flags)
    # items = DisposalItem.objects.all()

    return render(request, 'disposal/disposal.html', {'items': items})

# --- ACTIVITY LOG ---
def history_log(request):
    logs = DisposalActivityLog.objects.all().order_by('-timestamp')
    return render(request, 'disposal/history.html', {'items': logs})

def finalize_removal(request, pk):
    # 1. Try to find it in DisposalItem first
    disposal_entry = DisposalItem.objects.filter(pk=pk).first()
    
    if disposal_entry:
        asset = disposal_entry.asset_ptr
        reason = disposal_entry.disposal_reason
    else:
        # 2. If not in DisposalItem, it's a direct Asset (from your status sync)
        asset = get_object_or_404(Asset, pk=pk)
        reason = "Marked for Disposal via Status Update"

    # 3. Update the Asset Status to 'Disposed' (ID 5)
    disposed_status = get_object_or_404(AssetStatus, status_id=5) # Match your field name!
    asset.status_id = disposed_status
    asset.save()

    # 4. Create the activity log for Removal History
    DisposalActivityLog.objects.create(
        user=request.user,
        asset=asset,
        action_type='REMOVE',
        disposal_reason=reason,
        description=f"Finalized disposal for {asset.model} ({asset.serial_no})"
    )

    # 5. Cleanup the DisposalItem entry if it existed
    if disposal_entry:
        disposal_entry.delete()

    messages.success(request, f"Asset {asset.serial_no} successfully disposed.")
    return redirect('disposal:history_log')