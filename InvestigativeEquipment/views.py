from django.shortcuts import render, redirect, get_object_or_404
from .models import InvestigativeDetails, ICSRecord
from config.models import Asset, AssetStatus, Category
from disposal.models import DisposalItem
from firearms.models import Firearm
from mobility.views import Vehicle
from disposal.models import DisposalItem
from communications.models import Communication
from InvestigativeEquipment.models import InvestigativeDetails
import datetime
import uuid
import requests
import json
from django.contrib import messages
from django.db.models import Q

SUPABASE_URL = "https://vamjajitzyspdyfxisac.supabase.co"
SUPABASE_KEY = "sb_publishable_mTj-PK3WV3ZPqGOii548Ng_EXvssL54"
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def supabase_insert(table, payload):
    """Helper to insert a row into a Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.post(url, headers=SUPABASE_HEADERS, data=json.dumps(payload))
    return resp
 
 
def investigative_view(request):
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])
    all_d = DisposalItem.objects.filter(
        asset_ptr__status_id=4 
    )
    all_i = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5]).count()
    
    current_user_role = request.user.userprofile.role
    
    if request.method == "POST":
        action = request.POST.get("action_type")

        # === CREATE NEW ITEM ===
        if action == "add":
            item_name = request.POST.get("item_name", "").strip()
            cat_name = request.POST.get("category", "").strip()
            sub_cat = request.POST.get("subcategory", "").strip()
            status_name = request.POST.get("status", "Available").strip()
            qty_to_add = int(request.POST.get('quantity', 1))
            par_id = request.POST.get("par_id", "").strip() or None

            if not item_name or not cat_name:
                messages.error(request, "Item name and category are required.")
                return redirect("InvestigativeEquipment:investigative_view")

            try:
                if par_id and Asset.objects.filter(property_no=par_id).exclude(status__status_name="BER").exists():
                    messages.error(request, f"❌ Property ID '{par_id}' is already in use by an active asset.")
                    return redirect("InvestigativeEquipment:investigative_view")

                category, _ = Category.objects.get_or_create(category_name=cat_name)
                status, _ = AssetStatus.objects.get_or_create(status_name=status_name)

                new_asset = Asset.objects.create(
                    date_acquired=datetime.date.today(),
                    property_no=par_id if par_id else f"PN-{uuid.uuid4().hex[:8]}",
                    serial_no=f"SN-{uuid.uuid4().hex[:10]}",
                    model=item_name,
                    category=category,
                    status=status,
                    quantity=qty_to_add
                )

                InvestigativeDetails.objects.create(
                    asset_id=new_asset, 
                    par_id=par_id, 
                    office=sub_cat
                )

                messages.success(request, f"✅ Successfully created {item_name}.")
                
            except Exception as e:
                messages.error(request, f"❌ Error creating item: {str(e)}")
                return redirect("InvestigativeEquipment:investigative_view")

        # === UPDATE ITEM ===
        elif action == "update":
            asset_id = request.POST.get("asset_id")
            new_quantity = request.POST.get("quantity")
            new_item_name = request.POST.get("item_name", "").strip()
            
            print(f"DEBUG: Update request - Asset ID: {asset_id}, Name: {new_item_name}, Qty: {new_quantity}")

            if not asset_id:
                messages.error(request, "Asset ID is missing.")
                return redirect("InvestigativeEquipment:investigative_view")

            try:
                asset = Asset.objects.get(pk=asset_id)
                
                old_name = asset.model
                if new_item_name:
                    asset.model = new_item_name
                if new_quantity and new_quantity.isdigit():
                    asset.quantity = int(new_quantity)
                
                asset.save()
                messages.success(request, f"✅ {old_name} has been updated successfully.")
                print(f"DEBUG: Successfully updated asset {asset_id}")
                
            except Asset.DoesNotExist:
                messages.error(request, "Asset not found.")
            except Exception as e:
                messages.error(request, f"❌ Update failed: {str(e)}")
                print(f"ERROR during update: {str(e)}")

        # === MOVE TO BER ===
        elif action == "delete":
            asset_pk = request.POST.get("asset_id")
            asset = get_object_or_404(Asset, pk=asset_pk)

            try:
                ber_status, _ = AssetStatus.objects.get_or_create(status_name="BER")
                asset.status = ber_status
                asset.save()

                now_iso = datetime.datetime.utcnow().isoformat()

                supabase_insert("disposal_disposalitems", {
                    "asset_ptr_id": asset.pk,
                    "days_overdue": 0,
                    "expiry_date": datetime.date.today().isoformat(),
                    "disposal_reason": "Marked as BER from Investigative Equipment",
                    "disposal_date": now_iso,
                    "processed_by": None,
                    "personnel_assigned": None,
                    "last_sync": now_iso,
                })

                supabase_insert("disposal_disposalactivitylog", {
                    "asset_id": asset.pk,
                    "action_type": "REMOVE",
                    "disposal_reason": "Marked as BER from Investigative Equipment",
                    "timestamp": now_iso,
                    "user_id": request.user.pk if request.user.is_authenticated else None,
                })

                messages.success(request, f"Asset {asset.model} successfully marked as BER.")
            except Exception as e:
                messages.error(request, f"System Error: {str(e)}")

        return redirect("InvestigativeEquipment:investigative_view")

    # ===================== GET REQUEST  =====================
    all_investigative = InvestigativeDetails.objects.select_related(
        "asset_id", "asset_id__category", "asset_id__status"
    ).exclude(asset_id__status__status_name="BER")
 
    low_stock_items = []
    low_stock_count = 0
    try:
        low_stock_items = all_investigative.filter(asset_id__quantity__lte=3)
        low_stock_count = low_stock_items.count()
    except:
        low_stock_count = 0
 
    category_filter = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()
 
    equipment_display = all_investigative
    if category_filter:
        equipment_display = equipment_display.filter(asset_id__category__category_name__iexact=category_filter)
    if status_filter:
        equipment_display = equipment_display.filter(asset_id__status__status_name__iexact=status_filter)
 
    try:
        disposal_count = DisposalItem.objects.count()
    except Exception:
        disposal_count = 0

    context = {
        "equipment": equipment_display,
        "total_count": all_investigative.count(),
        "in_use": all_investigative.filter(asset_id__status__status_name__iexact="Issued").count(),
        "under_repair": all_investigative.filter(asset_id__status__status_name__iexact="Maintenance").count(),
        "selected_category": category_filter,
        "selected_status": status_filter,
        "low_stock_items": low_stock_items,
        "low_stock_count": low_stock_count,
        "disposal_count": disposal_count,
        'total_comms': all_c.count(),
        'total_firearms': all_f.count(),
        'total_vehicle': visible_v.count(),
        'total_ber': all_d.count(),
        'total_inves': all_i,
        'current_user_role':  current_user_role,
    }
    return render(request, "InvestigativeEquipment/investigative.html", context)
 

 
def par_monitoring_view(request):
    par_list = InvestigativeDetails.objects.select_related("asset_id", "asset_id__category").all()
 
    search_query = request.GET.get('search', '')
    if search_query:
        par_list = par_list.filter(
            Q(office__icontains=search_query) |
            Q(asset_id__model__icontains=search_query)
        )
 
    all_investigative = InvestigativeDetails.objects.all()
 
    context = {
        "par_list": par_list,
        "current_page": "par_monitoring",
        "total_count": all_investigative.count(),
    }
    return render(request, "par_monitoring.html", context)
 
 
def edit_par_view(request, pk):
    record = get_object_or_404(InvestigativeDetails, pk=pk)
 
    if request.method == "POST":
        record.office = request.POST.get("office", record.office)
        record.save()
        messages.success(request, "PAR record updated successfully.")
        return redirect("InvestigativeEquipment:par_monitoring")
 
    return render(request, "edit_par.html", {"record": record})
 
 
def delete_par_view(request, pk):
    record = get_object_or_404(InvestigativeDetails, pk=pk)
    record.delete()
    messages.success(request, "PAR record deleted.")
    return redirect("InvestigativeEquipment:par_monitoring")
 
 
def print_par_view(request, pk):
    record = get_object_or_404(InvestigativeDetails, pk=pk)
    asset = record.asset_id
 
    class ParContext:
        pass
 
    par = ParContext()
    par.par_number = record.par_id or asset.property_no
    par.fund_cluster = ""
    par.issued_to = record.office or "Unassigned"
    par.designation = ""
    par.date_issued = asset.date_acquired
    par.expiry_date = None
    par.remarks = ""
    par.purpose = "For official use of RFU 10"
    par.reference_no = ""
 
    class CommProxy:
        pass
 
    comm = CommProxy()
    comm.type = asset.model
    comm.imei_serial = asset.serial_no
    comm.frequency_range = ""
    comm.stock_level = asset.quantity
    comm.property_no = asset.property_no
    comm.date_acquired = asset.date_acquired
 
    par.communication = comm
 
    return render(request, "InvestigativeEquipment/print_par.html", {"par": par})
 
 
 
def ics_monitoring_view(request):
    all_investigative = InvestigativeDetails.objects.all()
 
    if request.method == "POST":
        ics_number = request.POST.get("ics_number", "").strip()
        asset_pk = request.POST.get("asset_pk", "").strip()
        reference_no = request.POST.get("reference_no", "").strip()
        issued_to = request.POST.get("issued_to", "").strip()
        date_issued = request.POST.get("date_issued") or None
        expiry_date = request.POST.get("expiry_date") or None
        remarks = request.POST.get("remarks", "").strip()
 
        asset = None
        if asset_pk:
            asset = get_object_or_404(Asset, pk=asset_pk)
 
        ICSRecord.objects.create(
            ics_number=ics_number,
            reference_no=reference_no,
            issued_to=issued_to,
            date_issued=date_issued,
            expiry_date=expiry_date,
            remarks=remarks,
            asset=asset,
        )
        messages.success(request, "ICS record saved successfully.")
        return redirect("InvestigativeEquipment:ics_monitoring")
 
    ics_list = ICSRecord.objects.select_related("asset").all()
 
    context = {
        "ics_list": ics_list,
        "par_list": all_investigative.select_related("asset_id"),
        "total_count": all_investigative.count(),
        "current_page": "ics_monitoring",
    }
    return render(request, "ics_monitoring.html", context)
 
 
def edit_ics_view(request, pk):
    record = get_object_or_404(ICSRecord, pk=pk)
    all_investigative = InvestigativeDetails.objects.select_related("asset_id").all()
 
    if request.method == "POST":
        record.ics_number = request.POST.get("ics_number", record.ics_number)
        record.reference_no = request.POST.get("reference_no", record.reference_no)
        record.issued_to = request.POST.get("issued_to", record.issued_to)
        record.date_issued = request.POST.get("date_issued") or record.date_issued
        record.expiry_date = request.POST.get("expiry_date") or record.expiry_date
        record.remarks = request.POST.get("remarks", record.remarks)
 
        asset_pk = request.POST.get("asset_pk")
        if asset_pk:
            record.asset = get_object_or_404(Asset, pk=asset_pk)
 
        record.save()
        messages.success(request, "ICS record updated successfully.")
        return redirect("InvestigativeEquipment:ics_monitoring")
 
    context = {
        "record": record,
        "par_list": all_investigative,
        "total_count": InvestigativeDetails.objects.count(),
    }
    return render(request, "edit_ics.html", context)
 
 
def delete_ics_view(request, pk):
    record = get_object_or_404(ICSRecord, pk=pk)
    record.delete()
    messages.success(request, "ICS record deleted.")
    return redirect("InvestigativeEquipment:ics_monitoring")
 
 
def print_ics_view(request, pk):
    record = get_object_or_404(ICSRecord, pk=pk)
    asset = record.asset
 
    class ICSContext:
        pass
 
    ics = ICSContext()
    ics.ics_number = record.ics_number
    ics.reference_no = record.reference_no
    ics.issued_to = record.issued_to
    ics.date_issued = record.date_issued
    ics.expiry_date = record.expiry_date
    ics.remarks = record.remarks
 
    class AssetProxy:
        pass
 
    a = AssetProxy()
    if asset:
        a.type = asset.model
        a.imei_serial = asset.serial_no
        a.property_no = asset.property_no
        a.date_acquired = asset.date_acquired
    else:
        a.type = "N/A"
        a.imei_serial = "-"
        a.property_no = "-"
        a.date_acquired = "-"
 
    ics.communication = a
 
    return render(request, "InvestigativeEquipment/print_ics.html", {"ics": ics})

def move_to_ber_investigative(request, item_id):
    asset = get_object_or_404(Asset, id=item_id)
    
    ber_status = get_object_or_404(AssetStatus, status_name="BER")
    
    asset.status = ber_status
    asset.save()
    
    messages.success(request, f"Asset {asset.model} has been moved to BER.")
    return redirect('InvestigativeEquipment:investigative_view')