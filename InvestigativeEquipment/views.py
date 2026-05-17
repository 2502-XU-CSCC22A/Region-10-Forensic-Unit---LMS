from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from django.utils import timezone

from .models import (
    InvestigativeDetails,
    ICSRecord,
    InvestigativePARRecord,
)

from .forms import InvestigativePARForm, InvestigativeICSForm

from config.models import Asset, AssetStatus, Category
from disposal.models import DisposalItem
from firearms.models import Firearm
from mobility.views import Vehicle
from communications.models import Communication

import datetime
import uuid


def create_investigative_activity_log(investigative_id, action, details):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO "Investigative_Activity_Log"
            (asset_ptr_id, action, details, created_at)
            VALUES (%s, %s, %s, NOW())
            """,
            [investigative_id, action, details],
        )


def get_common_counts(request):
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=["BER", "Disposed"])
    all_d = DisposalItem.objects.filter(asset_ptr__status_id=4)
    all_i = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5]).count()

    return {
        "total_comms": all_c.count(),
        "total_firearms": all_f.count(),
        "total_vehicle": visible_v.count(),
        "total_vehicles": visible_v.count(),
        "total_ber": all_d.count(),
        "total_inves": all_i,
        "current_user_role": request.user.userprofile.role,
    }


def investigative_view(request):
    common_counts = get_common_counts(request)

    if request.method == "POST":
        action = request.POST.get("action_type")

        if action == "add":
            item_name = request.POST.get("item_name", "").strip()
            cat_name = request.POST.get("category", "").strip()
            sub_cat = request.POST.get("subcategory", "").strip()
            status_name = request.POST.get("status", "Available").strip()
            qty_to_add = int(request.POST.get("quantity", 1))
            par_id = request.POST.get("par_id", "").strip() or None

            if not item_name or not cat_name:
                messages.error(request, "Item name and category are required.")
                return redirect("InvestigativeEquipment:investigative_view")

            try:
                if (
                    par_id
                    and Asset.objects.filter(property_no=par_id)
                    .exclude(status__status_name="BER")
                    .exists()
                ):
                    messages.error(
                        request,
                        f"❌ Property ID '{par_id}' is already in use by an active asset.",
                    )
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
                    quantity=qty_to_add,
                )

                InvestigativeDetails.objects.create(
                    asset_id=new_asset,
                    par_id=par_id,
                    office=sub_cat,
                )

                create_investigative_activity_log(
                    new_asset.id,
                    "Investigative Asset Created",
                    f"Added {new_asset.model} with Property No. {new_asset.property_no}.",
                )

                messages.success(request, f"✅ Successfully created {item_name}.")

            except Exception as e:
                messages.error(request, f"❌ Error creating item: {str(e)}")

            return redirect("InvestigativeEquipment:investigative_view")

        elif action == "update":
            asset_id = request.POST.get("asset_id")
            new_quantity = request.POST.get("quantity")
            new_item_name = request.POST.get("item_name", "").strip()
            new_status = request.POST.get("status", "").strip()

            if not asset_id:
                messages.error(request, "Asset ID is missing.")
                return redirect("InvestigativeEquipment:investigative_view")

            try:
                asset = Asset.objects.get(pk=asset_id)
                old_name = asset.model

                changes = []

                if new_item_name and asset.model != new_item_name:
                    changes.append(
                        f'Name changed from "{asset.model}" to "{new_item_name}"'
                    )
                    asset.model = new_item_name

                if (
                    new_quantity
                    and new_quantity.isdigit()
                    and asset.quantity != int(new_quantity)
                ):
                    changes.append(
                        f'Quantity changed from "{asset.quantity}" to "{new_quantity}"'
                    )
                    asset.quantity = int(new_quantity)

                if new_status:
                    status, _ = AssetStatus.objects.get_or_create(
                        status_name=new_status
                    )
                    if asset.status != status:
                        changes.append(f'Status changed to "{new_status}"')
                        asset.status = status

                asset.save()

                if changes:
                    create_investigative_activity_log(
                        asset.id,
                        "Investigative Asset Updated",
                        "; ".join(changes),
                    )

                messages.success(
                    request, f"✅ {old_name} has been updated successfully."
                )

            except Asset.DoesNotExist:
                messages.error(request, "Asset not found.")
            except Exception as e:
                messages.error(request, f"❌ Update failed: {str(e)}")

            return redirect("InvestigativeEquipment:investigative_view")

    all_investigative = InvestigativeDetails.objects.select_related(
        "asset_id",
        "asset_id__category",
        "asset_id__status",
    ).exclude(asset_id__status__status_name="BER")

    low_stock_items = all_investigative.filter(asset_id__quantity__lte=3)
    low_stock_count = low_stock_items.count()

    category_filter = request.GET.get("category", "").strip()
    status_filter = request.GET.get("status", "").strip()

    equipment_display = all_investigative

    if category_filter:
        equipment_display = equipment_display.filter(
            asset_id__category__category_name__iexact=category_filter
        )

    if status_filter:
        equipment_display = equipment_display.filter(
            asset_id__status__status_name__iexact=status_filter
        )

    context = {
        **common_counts,
        "equipment": equipment_display,
        "total_count": all_investigative.count(),
        "in_use": all_investigative.filter(
            asset_id__status__status_name__iexact="Issued"
        ).count(),
        "under_repair": all_investigative.filter(
            asset_id__status__status_name__iexact="Maintenance"
        ).count(),
        "selected_category": category_filter,
        "selected_status": status_filter,
        "low_stock_items": low_stock_items,
        "low_stock_count": low_stock_count,
        "disposal_count": DisposalItem.objects.count(),
    }

    return render(request, "InvestigativeEquipment/investigative.html", context)


def par_monitoring_view(request):
    common_counts = get_common_counts(request)

    pars = (
        InvestigativePARRecord.objects.select_related("asset").all().order_by("-par_id")
    )

    today = timezone.now().date()

    for par in pars:
        par.days_until_expiry = (
            (par.expiry_date - today).days if par.expiry_date else 9999
        )

    if request.method == "POST":
        p_form = InvestigativePARForm(request.POST)

        if p_form.is_valid():
            par = p_form.save()

            create_investigative_activity_log(
                par.asset.id,
                "Created PAR Record",
                f"PAR {par.par_number} was created for {par.asset.model} issued to {par.issued_to}.",
            )

            return redirect("InvestigativeEquipment:par_monitoring")
        else:
            print("PAR FORM ERRORS:", p_form.errors)

    else:
        p_form = InvestigativePARForm()

    return render(
        request,
        "InvestigativeEquipment/par_monitoring.html",
        {
            **common_counts,
            "p_form": p_form,
            "pars": pars,
            "today": today,
            "current_page": "par_monitoring",
        },
    )


def edit_par_view(request, pk):
    record = get_object_or_404(
        InvestigativePARRecord.objects.select_related("asset"),
        pk=pk,
    )

    if request.method == "POST":
        form = InvestigativePARForm(request.POST, instance=record)

        if form.is_valid():
            par = form.save()

            create_investigative_activity_log(
                par.asset.id,
                "Updated PAR Record",
                f"PAR {par.par_number} was updated for {par.asset.model}.",
            )

            return redirect("InvestigativeEquipment:par_monitoring")
        else:
            print("EDIT PAR FORM ERRORS:", form.errors)

    else:
        form = InvestigativePARForm(instance=record)

    return render(
        request,
        "InvestigativeEquipment/edit_par.html",
        {
            "form": form,
            "record": record,
        },
    )


def delete_par_view(request, pk):
    record = get_object_or_404(
        InvestigativePARRecord.objects.select_related("asset"),
        pk=pk,
    )

    investigative_id = record.asset.id
    par_number = record.par_number
    issued_to = record.issued_to
    asset_name = record.asset.model

    record.delete()

    create_investigative_activity_log(
        investigative_id,
        "Deleted PAR Record",
        f"PAR {par_number} for {asset_name}, issued to {issued_to}, was deleted from the PAR registry.",
    )

    return redirect("InvestigativeEquipment:par_monitoring")


def print_par_view(request, pk):
    par = get_object_or_404(
        InvestigativePARRecord.objects.select_related("asset"),
        pk=pk,
    )

    create_investigative_activity_log(
        par.asset.id,
        "Printed PAR Record",
        f"PAR {par.par_number} for {par.asset.model} was opened for printing.",
    )

    return render(request, "InvestigativeEquipment/print_par.html", {"par": par})


def ics_monitoring_view(request):
    common_counts = get_common_counts(request)

    icss = ICSRecord.objects.select_related("asset").all().order_by("-ics_id")

    today = timezone.now().date()

    for ics in icss:
        ics.days_until_expiry = (
            (ics.expiry_date - today).days if ics.expiry_date else 9999
        )

    if request.method == "POST":
        i_form = InvestigativeICSForm(request.POST)

        if i_form.is_valid():
            ics = i_form.save()

            create_investigative_activity_log(
                ics.asset.id,
                "Created ICS Record",
                f"ICS {ics.ics_number} was created for {ics.asset.model} issued to {ics.issued_to}.",
            )

            return redirect("InvestigativeEquipment:ics_monitoring")
        else:
            print("ICS FORM ERRORS:", i_form.errors)

    else:
        i_form = InvestigativeICSForm()

    return render(
        request,
        "InvestigativeEquipment/ics_monitoring.html",
        {
            **common_counts,
            "i_form": i_form,
            "icss": icss,
            "today": today,
            "current_page": "ics_monitoring",
        },
    )


def edit_ics_view(request, pk):
    record = get_object_or_404(
        ICSRecord.objects.select_related("asset"),
        pk=pk,
    )

    if request.method == "POST":
        form = InvestigativeICSForm(request.POST, instance=record)

        if form.is_valid():
            ics = form.save()

            create_investigative_activity_log(
                ics.asset.id,
                "Updated ICS Record",
                f"ICS {ics.ics_number} was updated for {ics.asset.model}.",
            )

            return redirect("InvestigativeEquipment:ics_monitoring")
        else:
            print("EDIT ICS FORM ERRORS:", form.errors)

    else:
        form = InvestigativeICSForm(instance=record)

    return render(
        request,
        "InvestigativeEquipment/edit_ics.html",
        {
            "form": form,
            "record": record,
        },
    )


def delete_ics_view(request, pk):
    record = get_object_or_404(
        ICSRecord.objects.select_related("asset"),
        pk=pk,
    )

    investigative_id = record.asset.id
    ics_number = record.ics_number
    issued_to = record.issued_to
    asset_name = record.asset.model

    record.delete()

    create_investigative_activity_log(
        investigative_id,
        "Deleted ICS Record",
        f"ICS {ics_number} for {asset_name}, issued to {issued_to}, was deleted from the ICS registry.",
    )

    return redirect("InvestigativeEquipment:ics_monitoring")


def print_ics_view(request, pk):
    ics = get_object_or_404(
        ICSRecord.objects.select_related("asset"),
        pk=pk,
    )

    create_investigative_activity_log(
        ics.asset.id,
        "Printed ICS Record",
        f"ICS {ics.ics_number} for {ics.asset.model} was opened for printing.",
    )

    return render(request, "InvestigativeEquipment/print_ics.html", {"ics": ics})


def move_to_ber_investigative(request, item_id):
    asset = get_object_or_404(Asset, pk=item_id)

    try:
        ber_status, _ = AssetStatus.objects.get_or_create(status_name="BER")

        asset.status = ber_status
        asset.save()

        pars_deleted = InvestigativePARRecord.objects.filter(asset_id=item_id).delete()[
            0
        ]

        ics_deleted = ICSRecord.objects.filter(asset_id=item_id).delete()[0]

        details = f"Investigative Asset ID {item_id} has been moved to BER"

        if pars_deleted and ics_deleted:
            details += ", and PAR and ICS Records are deleted"

        elif pars_deleted:
            details += ", and PAR Record is deleted"

        elif ics_deleted:
            details += ", and ICS Record is deleted"

        create_investigative_activity_log(
            item_id,
            "Moved to BER",
            details,
        )

        messages.success(request, "Asset successfully moved to BER.")

    except Exception as e:
        messages.error(request, f"Error moving asset to BER: {str(e)}")

    return redirect("InvestigativeEquipment:investigative_view")


def activity_logs(request):
    common_counts = get_common_counts(request)

    return render(
        request,
        "InvestigativeEquipment/activity_logs.html",
        common_counts,
    )
