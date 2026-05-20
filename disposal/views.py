import requests
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.contenttypes.models import ContentType
from mobility.models import Vehicle
from communications.models import Communication
from config.models import Asset, AssetStatus, Personnel
from InvestigativeEquipment.models import InvestigativeDetails
from firearms.models import Firearm
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

def disposal_list(request):
    all_items = DisposalItem.objects.select_related(
        'asset_ptr', 
        'asset_ptr__category'
    ).filter(status_id=4).order_by('-disposal_date')

    paginator = Paginator(all_items, 5)
    page_number = request.GET.get('page')
    disposal_items = paginator.get_page(page_number)
    
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearms_all = Firearm.objects.count()
    
    current_user_role = request.user.userprofile.role
    inves_all = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5]).count()
    
    logs = DisposalActivityLog.objects.all().order_by('-timestamp')
    
    last_item = DisposalItem.objects.order_by('-last_sync').first()
    sync_time = last_item.last_sync if last_item else None
    
    today = timezone.now().date()
        
    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None
  
    ber_today_count = DisposalItem.objects.filter(
        disposal_date__date=today
    ).count()
    
    comms_ber = DisposalItem.objects.filter(
        asset_ptr__status__status_id='4',
        asset_ptr__category__category_name='communications'
    ).count()
    
    vehicle_category = ['mobility', 'VEHICLE']
    
    mobility_ber = DisposalItem.objects.filter(
        asset_ptr__status__status_id='4',
        asset_ptr__category__category_name__in=vehicle_category
    ).count()
    
    firearms_ber = DisposalItem.objects.filter(
        asset_ptr__status__status_id='4',
        asset_ptr__category__category_name='firearms'
    ).count()
    
    target_categories = ['investigative_equipment', 'Technical Sections', 'Fingerprint Kit', 'Forensics', 'Photography']
    
    inves_ber = DisposalItem.objects.filter(
        asset_ptr__status__status_id='4',
        asset_ptr__category__category_name__in=target_categories
    ).count()
    
    total_ber = DisposalItem.objects.filter(
        asset_ptr__status__status_id='4',
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
        'items': disposal_items,
        'logs': logs,
        'last_sync_time': sync_time,
        'ber_today_count': ber_today_count,
        'current_time': timezone.now(),
        'comms_ber': comms_ber,
        'firearms_ber': firearms_ber,
        'mobility_ber': mobility_ber,
        'inves_ber': inves_ber,
        'total_ber': total_ber,
        'disposal_items': disposal_items,
        'total_vehicle': visible_v.count(),
        'comms_all': comms_all,
        'total_removed': len(disposal_items),
        'firearms_all': firearms_all,
        'inves_all': inves_all,
        'current_user_role': current_user_role,
    })

def history_log(request):
    logs = DisposalActivityLog.objects.all().order_by('-timestamp')
    
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearms_all = Firearm.objects.count()
    
    current_user_role = request.user.userprofile.role
    inves_all = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5]).count()
    
    total_ber = DisposalItem.objects.filter(asset_ptr__status_id=4).count()
    current_user_role = request.user.userprofile.role
    
    return render(request, 'disposal/history.html', {
        'items': logs,
        'firearms_all': firearms_all,
        'inves_all': inves_all,
        'current_user_role': current_user_role,
        'total_vehicle': visible_v.count(),
        'comms_all': comms_all,
        'total_ber': total_ber,
    })

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

    if hasattr(asset, 'asset_ptr_id') and asset.asset_ptr_id:
        parent_asset_id = asset.asset_ptr_id
    elif hasattr(asset, 'asset_ptr') and asset.asset_ptr:
        parent_asset_id = asset.asset_ptr.id
    else:
        parent_asset_id = asset.id

    description = f"Finalized disposal for {asset.model} ({asset.serial_no}) fa-trash-alt"

    DisposalActivityLog.objects.create(
        user=request.user,
        asset_id=parent_asset_id,
        action_type='REMOVE',
        disposal_reason=reason,
        description=description
    )

    # 2. Push to Supabase with explicitly aligned fields
    supabase_url = "https://vamjajitzyspdyfxisac.supabase.co/rest/v1/disposal_disposalactivitylog"
    supabase_headers = {
        "apikey": "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54",
        "Authorization": "Bearer sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    supabase_data = {
        "asset_id": parent_asset_id, 
        "action_type": "REMOVE",
        "disposal_reason": reason,
        "description": description,
        "user_id": request.user.id,
        "timestamp": timezone.now().isoformat()
    }
    
    try:
        requests.post(supabase_url, headers=supabase_headers, json=supabase_data, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Failed to sync log to Supabase: {e}")

    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(Asset).id,
        object_id=asset.id,
        object_repr=f"{asset.category.category_name if asset.category else 'Asset'} – {asset.property_no}",
        action_flag=DELETION,
        change_message=f"Disposed asset. Reason: {reason}"
    )

    messages.success(request, f"Asset {asset.serial_no} successfully disposed.")
    return redirect('disposal:history_log')