from datetime import timedelta
from django.utils import timezone
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.admin.models import LogEntry

from config.models import Asset
from disposal.models import DisposalItem
from mobility.models import Vehicle, ActivityLog
from firearms.models import Firearm
from InvestigativeEquipment.models import InvestigativeDetails
from InvestigativeEquipment.models import InvestigativePARRecord
from communications.models import Communication
from communications.models import CommunicationActivityLog
from firearms.models import FirearmActivityLog

User = get_user_model()


def _role_label(user):
    try:
        return user.userprofile.role
    except Exception:
        return "User"


@login_required
def dashboard_view(request):
    # --- Existing Counts ---
    total_asset = Asset.objects.exclude(status__in=[4, 5])
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=["BER", "Disposed"])
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearms_all = Firearm.objects.count()
    inves_all = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5])
    total_ber = DisposalItem.objects.filter(asset_ptr__status_id=4).count()

    try:
        current_user_role = request.user.userprofile.role
    except Exception:
        current_user_role = _role_label(request.user)

    # --- Session Tracking for Unread ---
    read_ids = set(request.session.get("read_activity_ids", []))

    # ==========================================
    # 1. RECENT ACTIVITIES WIDGET (Logins/Logouts)
    # ==========================================
    # Filters logs specifically containing login/logout keywords
    login_logs = (
        LogEntry.objects.select_related("user")
        .filter(
            Q(change_message__icontains="logged in")
            | Q(change_message__icontains="logged out")
        )
        .order_by("-action_time")[:5]
    )

    recent_activities = []
    for entry in login_logs:
        u = entry.user
        name = u.get_full_name() or u.username
        role = _role_label(u)

        recent_activities.append(
            {
                "id": entry.id,
                "actor": f"{name} ({role})",
                "action": entry.change_message,
                # Exact date and time format: e.g., "Oct 24, 2026"
                "timestamp": entry.action_time.strftime("%b %d, %Y"),
                "unread": entry.id not in read_ids,
            }
        )

    # ==========================================
    # 2. ASSETS WIDGET (ALL MODULE LOGS)
    # ==========================================

    asset_activities = []

    # ==========================================
    # COMMUNICATIONS LOGS
    # ==========================================

    communication_logs = CommunicationActivityLog.objects.select_related(
        "communication"
    ).order_by("-created_at")[:10]

    for log in communication_logs:

        asset_activities.append(
            {
                "id": f"comm-{log.id}",
                "actor": "Communications",
                "action": log.action,
                "item": log.details,
                "timestamp_raw": log.created_at,
                "timestamp": log.created_at.strftime("%b %d, %Y, %I:%M %p"),
                "unread": str(log.id) not in read_ids,
            }
        )


# ==========================================
# FIREARMS LOGS
# ==========================================

    try:

        firearm_logs = FirearmActivityLog.objects.all().order_by("-created_at")[:10]

        for log in firearm_logs:

            asset_activities.append(
                {
                    "id": f"firearm-{log.id}",
                    "actor": "Firearms",
                    "action": log.action,
                    "item": log.details,
                    "timestamp_raw": log.created_at,
                    "timestamp": log.created_at.strftime("%b %d, %Y, %I:%M %p"),
                    "unread": True,
                }
            )

    except Exception as e:
        print("FIREARM LOG ERROR:", e)
        
        # ==========================================
# MOBILITY LOGS
# ==========================================

    try:
        mobility_logs = ActivityLog.objects.all().order_by("-timestamp")[:10]

        for log in mobility_logs:
            asset_activities.append(
                {
                    "id": f"mobility-{log.id}",
                    "actor": "Mobility",
                    "action": log.action_type,
                    "item": log.description,
                    "timestamp_raw": log.timestamp,
                    "timestamp": log.timestamp.strftime("%b %d, %Y, %I:%M %p"),
                    "unread": True,
                }
            )

    except Exception as e:
        print("MOBILITY LOG ERROR:", e)

    # ==========================================
    # SORT ALL LOGS BY NEWEST
    # ==========================================

    asset_activities = sorted(
        asset_activities,
        key=lambda x: x["timestamp_raw"],
        reverse=True
    )

    # SHOW ONLY LATEST 7
    asset_activities = asset_activities[:7]

    # ==========================================
    # 3. NOTIFICATIONS WIDGET (Multi-table PAR Expirations)
    # ==========================================
    today = timezone.now().date()
    one_month_from_now = today + timedelta(days=30)

    expiring_notifications = []

    # ── A. Investigative Equipment Expirations ──
    # Query the PAR table directly for records expiring within 30 days
    investigative_expiring = InvestigativePARRecord.objects.filter(
        expiry_date__range=[today, one_month_from_now]
    ).select_related(
        "asset"
    )  # This pulls the parent config_asset data in one query

    for par in investigative_expiring:
        # Safely extract the asset relation
        asset = par.asset

        # Fallback name logic: use the asset's model/property number if available
        asset_name = (
            f"Investigative: {asset.model}"
            if asset and asset.model
            else "Investigative Asset"
        )
        serial_no = asset.serial_no if asset else (par.par_number or "N/A")

        expiring_notifications.append(
            {
                "asset_name": asset_name,
                "serial_number": serial_no,
                "expiry_date": par.expiry_date.strftime("%b %d, %Y"),
            }
        )

    # ── B. Mobility / Vehicle Expirations ──
    mobility_expiring = Vehicle.objects.filter(
        par_records__expiry_date__range=[today, one_month_from_now]
    ).distinct()

    for vehicle in mobility_expiring:
        pars = vehicle.par_records_set.filter(
            expiry_date__range=[today, one_month_from_now]
        )
        for par in pars:
            expiring_notifications.append(
                {
                    "asset_name": f"Vehicle: {vehicle.make_model}",
                    "serial_number": vehicle.plate_number
                    or vehicle.conduction_number
                    or "N/A",
                    "expiry_date": par.expiry_date.strftime("%b %d, %Y"),
                }
            )

    # ── C. Communications Expirations ──
    comms_expiring = Communication.objects.filter(
        communication_par_record__expiry_date__range=[today, one_month_from_now]
    ).distinct()

    for comm in comms_expiring:
        pars = comm.communication_par_record_set.filter(
            expiry_date__range=[today, one_month_from_now]
        )
        for par in pars:
            expiring_notifications.append(
                {
                    "asset_name": f"Comms: {comm.type}",
                    "serial_number": comm.imei_serial or "N/A",
                    "expiry_date": par.expiry_date.strftime("%b %d, %Y"),
                }
            )

    # ── D. Firearms Expirations ──
    firearms_expiring = Firearm.objects.filter(
        firearms_par_records__expiry_date__range=[today, one_month_from_now]
    ).distinct()

    for firearm in firearms_expiring:
        pars = firearm.firearms_par_records_set.filter(
            expiry_date__range=[today, one_month_from_now]
        )
        for par in pars:
            expiring_notifications.append(
                {
                    "asset_name": f"Firearm: {firearm.type}",
                    "serial_number": getattr(firearm, "faid_serial", "N/A"),
                    "expiry_date": par.expiry_date.strftime("%b %d, %Y"),
                }
            )

    # Sort all gathered expiry alerts chronologically
    expiring_notifications.sort(
        key=lambda x: timezone.datetime.strptime(x["expiry_date"], "%b %d, %Y")
    )

    # Combined unread count for UI badges
    unread_count = sum(1 for a in recent_activities if a["unread"]) + sum(
        1 for a in asset_activities if a["unread"]
    )

    context = {
        "total_assets": total_asset.count(),
        "total_firearms": firearms_all,
        "total_mobility": visible_v.count(),
        "total_communications": comms_all,
        "total_investigative": inves_all.count(),
        "total_ber": total_ber,
        "recent_activities": recent_activities,  # Target this in template for logins
        "asset_activities": asset_activities,  # Target this for the assets widget
        "expiring_notifications": expiring_notifications,  # Target this for expiry alerts
        "current_user_role": current_user_role,
        "notification_count": unread_count,
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
@require_POST
def mark_all_read(request):
    # Dynamically grab the newest items to update session reading history
    recent_ids = list(
        LogEntry.objects.order_by("-action_time").values_list("id", flat=True)[:35]
    )

    existing = set(request.session.get("read_activity_ids", []))
    existing.update(recent_ids)

    request.session["read_activity_ids"] = list(existing)
    request.session.modified = True

    return JsonResponse({"status": "ok", "read_count": len(recent_ids)})


@login_required
def recent_activities_api(request):
    # Base filter for login/logout actions only
    logs = (
        LogEntry.objects.select_related("user")
        .filter(
            Q(change_message__icontains="logged in")
            | Q(change_message__icontains="logged out")
        )
        .order_by("-action_time")
    )

    # --- Apply Dynamic Filters ---
    date_filter = request.GET.get("date")  # Format expected: YYYY-MM-DD
    role_filter = request.GET.get("role")  # Expecting: Admin, Logistics Officer, etc.

    if date_filter:
        logs = logs.filter(action_time__date=date_filter)

    if role_filter:
        # Checking against the custom usermanagement_userprofile configuration
        logs = logs.filter(user__userprofile__role__iexact=role_filter)

    # --- Pagination Setup (10 items per page) ---
    page_number = request.GET.get("page", 1)
    paginator = Paginator(logs, 10)
    page_obj = paginator.get_page(page_number)

    # Format data structurally for JavaScript consumption
    activities_list = []
    for entry in page_obj:
        u = entry.user
        name = u.get_full_name() or u.username
        try:
            role = u.userprofile.role
        except Exception:
            role = "User"

        activities_list.append(
            {
                "actor": f"{name} ({role})",
                "action": entry.change_message,
                "timestamp": entry.action_time.strftime("%b %d, %Y, %I:%M %p"),
                "is_logout": "out" in entry.change_message.lower(),
            }
        )

    return JsonResponse(
        {
            "results": activities_list,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "number": page_obj.number,
            "num_pages": paginator.num_pages,
        }
    )


@login_required
def asset_activities_api(request):
    """API Endpoint for the Assets Widget Modal History"""
    # Exclude login/logout logs to isolate asset CRUD events
    logs = (
        LogEntry.objects.select_related("user", "content_type")
        .exclude(
            Q(change_message__icontains="logged in")
            | Q(change_message__icontains="logged out")
        )
        .order_by("-action_time")
    )

    # --- Apply Filters ---
    date_filter = request.GET.get("date")
    role_filter = request.GET.get("role")
    action_filter = request.GET.get("action")  # "Added", "Edited/Moved", "Deleted"

    if date_filter:
        logs = logs.filter(action_time__date=date_filter)
    if role_filter:
        logs = logs.filter(user__userprofile__role__iexact=role_filter)
    if action_filter:
        ACTION_FLAG_MAP = {
            "Added": ADDITION,
            "Edited/Moved": CHANGE,
            "Deleted": DELETION,
        }
        if action_filter in ACTION_FLAG_MAP:
            logs = logs.filter(action_flag=ACTION_FLAG_MAP[action_filter])

    # --- Paginate (10 items per page) ---
    page_number = request.GET.get("page", 1)
    paginator = Paginator(logs, 10)
    page_obj = paginator.get_page(page_number)

    ACTION_TEXT_MAP = {ADDITION: "Added", CHANGE: "Edited/Moved", DELETION: "Deleted"}

    results = []
    for entry in page_obj:
        u = entry.user
        name = u.get_full_name() or u.username
        role = (
            getattr(u.userprofile, "role", "User")
            if hasattr(u, "userprofile")
            else "User"
        )

        action_text = ACTION_TEXT_MAP.get(entry.action_flag, "Modified")
        if "moved" in str(entry.change_message).lower():
            action_text = "Moved"

        results.append(
            {
                "actor": f"{name} ({role})",
                "action": action_text,
                "item": entry.object_repr,
                "timestamp": entry.action_time.strftime("%b %d, %Y, %I:%M %p"),
            }
        )

    return JsonResponse(
        {
            "results": results,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "number": page_obj.number,
            "num_pages": paginator.num_pages,
        }
    )


@login_required
def notifications_api(request):
    """API Endpoint for the Notifications Widget Modal History (All near-expiry PARs)"""
    today = timezone.now().date()
    one_month_from_now = today + timedelta(days=30)

    # Optional category filter chosen from the modal dropdown
    category_filter = request.GET.get("category", "").lower()
    all_expiring = []

    # 1. Investigative
    if not category_filter or category_filter == "investigative":
        for par in InvestigativePARRecord.objects.filter(
            expiry_date__range=[today, one_month_from_now]
        ).select_related("asset_id"):
            all_expiring.append(
                {
                    "category": "Investigative",
                    "asset_name": (
                        par.asset_id.model if par.asset_id else "Investigative Asset"
                    ),
                    "serial_number": (
                        par.asset_id.serial_no
                        if par.asset_id
                        else (par.par_number or "N/A")
                    ),
                    "expiry_date": par.expiry_date,
                }
            )

    # 2. Mobility
    if not category_filter or category_filter == "mobility":
        for par in Vehicle.objects.filter(
            expiry_date__range=[today, one_month_from_now]
        ).select_related("vehicle"):
            all_expiring.append(
                {
                    "category": "Mobility",
                    "asset_name": (
                        par.vehicle.make_model if par.vehicle else "Unknown Vehicle"
                    ),
                    "serial_number": (
                        par.vehicle.plate_number
                        if par.vehicle
                        else (par.par_number or "N/A")
                    ),
                    "expiry_date": par.expiry_date,
                }
            )

    # 3. Communications
    if not category_filter or category_filter == "communications":
        for par in Communication.objects.filter(
            expiry_date__range=[today, one_month_from_now]
        ).select_related("communication"):
            all_expiring.append(
                {
                    "category": "Communications",
                    "asset_name": (
                        par.communication.type if par.communication else "Device"
                    ),
                    "serial_number": (
                        par.communication.imei_serial
                        if par.communication
                        else (par.par_number or "N/A")
                    ),
                    "expiry_date": par.expiry_date,
                }
            )

    # 4. Firearms
    if not category_filter or category_filter == "firearms":
        for par in Firearm.objects.filter(
            expiry_date__range=[today, one_month_from_now]
        ).select_related("firearm"):
            all_expiring.append(
                {
                    "category": "Firearms",
                    "asset_name": par.firearm.type if par.firearm else "Weapon",
                    "serial_number": getattr(
                        par.firearm, "faid_serial", par.par_number or "N/A"
                    ),
                    "expiry_date": par.expiry_date,
                }
            )

    # Sort comprehensively by closest date
    all_expiring.sort(key=lambda x: x["expiry_date"])

    # Since this aggregates across multiple databases in memory, we slice manually using Paginator
    page_number = int(request.GET.get("page", 1))
    paginator = Paginator(all_expiring, 10)
    page_obj = paginator.get_page(page_number)

    results = [
        {
            "category": x["category"],
            "asset_name": x["asset_name"],
            "serial_number": x["serial_number"],
            "expiry_date": x["expiry_date"].strftime("%b %d, %Y"),
        }
        for x in page_obj
    ]

    return JsonResponse(
        {
            "results": results,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "number": page_obj.number,
            "num_pages": paginator.num_pages,
        }
    )
