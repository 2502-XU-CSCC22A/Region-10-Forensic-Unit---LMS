from django.shortcuts import render, redirect, get_object_or_404
from .models import InvestigativeDetails
from config.models import Asset, AssetStatus, Category
from mobility.models import Vehicle
from disposal.models import DisposalItem
from communications.models import Communication
from InvestigativeEquipment.models import InvestigativeDetails
from firearms.models import Firearm
import datetime
import uuid
from django.contrib import messages
from django.contrib.auth.models import User

def investigative_view(request):
    vehicle_all = Vehicle.objects.count()
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    disposal_all = DisposalItem.objects.exclude(status_id__in=[5])
    firearm_all = Firearm.objects.exclude(status_id__in=[4, 5]).count()
    inves_all = InvestigativeDetails.objects.count()
    
    users = User.objects.select_related('userprofile') \
        .filter(is_active=True) \
        .order_by('-last_login')[:50]
        
    try:
        current_user_role = request.user.userprofile.role
        print("USER DEBUG:", repr(request.user.username))
        print("ROLE DEBUG:", repr(current_user_role))
    except Exception as e:
        print("ROLE ERROR:", e)
        current_user_role = None
    
    if request.method == "POST":
        action = request.POST.get("action_type")

        if action == "add":
            item_name = request.POST.get("item_name", "").strip()
            item_description = request.POST.get("item_description", "").strip() or None
            par_id = request.POST.get("par_id", "").strip() or None
            cat_name = request.POST.get("category", "").strip()
            status_name = request.POST.get("status", "Available").strip() or "Available"
            office = request.POST.get("office", "").strip() or None

            if not item_name and item_description:
                item_name = item_description

            if item_name and cat_name:
                category, _ = Category.objects.get_or_create(category_name=cat_name)
                status, _ = AssetStatus.objects.get_or_create(status_name=status_name)

                new_asset = Asset.objects.create(
                    date_acquired=datetime.date.today(),
                    property_no=f"PN-{uuid.uuid4().hex[:8]}",
                    serial_no=f"SN-{uuid.uuid4().hex[:10]}",
                    model=item_name,
                    category=category,
                    status=status,
                    office=office
                )

                InvestigativeDetails.objects.create(
                    asset_id=new_asset,
                    item_description=item_description,
                    par_id=par_id
                )

            messages.success(request, "Equipment added successfully.")
            return redirect("InvestigativeEquipment:investigative_view")

        elif action == "update":
            asset_pk = request.POST.get("asset_id")
            item_name = request.POST.get("item_name", "").strip()
            status_name = request.POST.get("status", "").strip()
            cat_name = request.POST.get("category", "").strip()
            item_description = request.POST.get("item_description", "").strip() or None
            par_id = request.POST.get("par_id", "").strip() or None

            asset = get_object_or_404(Asset, pk=asset_pk)
            status = get_object_or_404(AssetStatus, status_name=status_name)

            if item_name:
                asset.model = item_name
            if cat_name:
                category, _ = Category.objects.get_or_create(category_name=cat_name)
                asset.category = category
            asset.status = status
            asset.save()

            details, _ = InvestigativeDetails.objects.get_or_create(asset_id=asset)
            details.item_description = item_description
            details.par_id = par_id
            details.save()

            messages.success(request, "Equipment updated successfully.")
            return redirect("InvestigativeEquipment:investigative_view")

        elif action == "delete":
            asset_pk = request.POST.get("asset_id")
            asset = get_object_or_404(Asset, pk=asset_pk)
            asset.delete()
            messages.success(request, "Equipment deleted successfully.")
            return redirect("InvestigativeEquipment:investigative_view")

    equipment_list = InvestigativeDetails.objects.select_related(
        "asset_id",
        "asset_id__category",
        "asset_id__status"
    ).all()

    category = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()

    if category:
        equipment_list = equipment_list.filter(
            asset_id__category__category_name__iexact=category
        )
    if status:
        equipment_list = equipment_list.filter(
            asset_id__status__status_name__iexact=status
        )

    context = {
        "equipment": equipment_list,
        "total_count": equipment_list.count(),
        "in_use": equipment_list.filter(asset_id__status__status_name="In Use").count(),
        "under_repair": equipment_list.filter(asset_id__status__status_name="Under Repair").count(),
        "selected_category": category,
        "selected_status": status,
        "active_page": 'firearms',
        "vehicle_all": vehicle_all,
        "comms_all": comms_all,
        "disposal_all": disposal_all,
        "firearm_all": firearm_all,
        "inves_all": inves_all,
        "current_user_role": current_user_role,
    }

    return render(request, "investigative.html", context)