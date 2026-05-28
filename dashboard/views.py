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

from config.models import Asset
from disposal.models import DisposalItem, DisposalActivityLog
from mobility.models import Vehicle, ActivityLog
from firearms.models import Firearm, FirearmActivityLog
from InvestigativeEquipment.models import InvestigativeDetails, InvestigativePARRecord, InvestigativeActivityLog
from communications.models import Communication, CommunicationActivityLog

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
                "timestamp": entry.action_time.strftime("%b %d, %Y"),
                "unread": entry.id not in read_ids,
            }
        )

    # ==========================================
    # 2. ASSETS WIDGET (ALL 5 MODULE LOGS)
    # ==========================================
    asset_activities = []

    # ── A. Communications Logs ──
    try:
        communication_logs = CommunicationActivityLog.objects.select_related("communication").order_by("-created_at")[:10]
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
    except Exception as e:
        print("COMMUNICATIONS LOG ERROR:", e)

    # ── B. Firearms Logs ──
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
                    "unread": str(log.id) not in read_ids,
                }
            )
    except Exception as e:
        print("FIREARM LOG ERROR:", e)

    # ── C. Mobility Logs ──
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
                    "unread": str(log.id) not in read_ids,
                }
            )
    except Exception as e:
        print("MOBILITY LOG ERROR:", e)

    # ── D. Investigative Equipment Logs ──
    try:
        investigative_logs = InvestigativeActivityLog.objects.select_related("asset").all().order_by("-created_at")[:10]
        for log in investigative_logs:
            asset_activities.append(
                {
                    "id": f"investigative-{log.log_id}",
                    "actor": "Investigative",
                    "action": log.action.replace("Investigative Asset ", ""),
                    "item": log.details,
                    "timestamp_raw": log.created_at,
                    "timestamp": log.created_at.strftime("%b %d, %Y, %I:%M %p"),
                    "unread": str(log.log_id) not in read_ids,
                }
            )
    except Exception as e:
        print("INVESTIGATIVE LOG ERROR:", e)

    # ── E. Disposal Logs ──
    try:
        disposal_logs = DisposalActivityLog.objects.select_related('user', 'asset').all().order_by("-timestamp")[:10]
        for log in disposal_logs:
            action_verb = "Removed" if log.action_type == 'REMOVE' else "Updated"
            asset_activities.append(
                {
                    "id": f"disposal-{log.id}",
                    "actor": "Disposal",
                    "action": action_verb,
                    "item": log.description.replace(" fa-trash-alt", ""),
                    "timestamp_raw": log.timestamp,
                    "timestamp": log.timestamp.strftime("%b %d, %Y, %I:%M %p"),
                    "unread": str(log.id) not in read_ids,
                }
            )
    except Exception as e:
        print("DISPOSAL LOG ERROR:", e)

    # --- Sort and Bound Asset Feed ---
    asset_activities = sorted(
        asset_activities,
        key=lambda x: x["timestamp_raw"],
        reverse=True
    )
    asset_activities = asset_activities[:5]

    # ==========================================
    # 3. NOTIFICATIONS WIDGET (PAR Expirations)
    # ==========================================
    today = timezone.now().date()
    one_month_from_now = today + timedelta(days=30)
    expiring_notifications = []

    # ── A. Investigative Equipment Expirations ──
    try:
        investigative_expiring = InvestigativePARRecord.objects.filter(
            expiry_date__range=[today, one_month_from_now]
        ).select_related("asset")

        for par in investigative_expiring:
            asset = par.asset
            asset_name = f"Investigative: {asset.model}" if asset and asset.model else "Investigative Asset"
            serial_no = asset.serial_no if asset else (par.par_number or "N/A")

            expiring_notifications.append(
                {
                    "asset_name": asset_name,
                    "serial_number": serial_no,
                    "expiry_date": par.expiry_date.strftime("%b %d, %Y"),
                }
            )
    except Exception as e:
        print("NOTIF INVESTIGATIVE ERROR:", e)

    # ── B. Mobility / Vehicle Expirations ──
    try:
        mobility_expiring = Vehicle.objects.filter(
            par_records__expiry_date__range=[today, one_month_from_now]
        ).distinct()

        for vehicle in mobility_expiring:
            pars = vehicle.par_records.filter(expiry_date__range=[today, one_month_from_now])
            for par in pars:
                expiring_notifications.append(
                    {
                        "asset_name": f"Vehicle: {vehicle.make_model}",
                        "serial_number": vehicle.plate_number or vehicle.conduction_number or "N/A",
                        "expiry_date": par.expiry_date.strftime("%b %d, %Y"),
                    }
                )
    except Exception as e:
        print("NOTIF MOBILITY ERROR:", e)

    # ── C. Communications Expirations ──
    try:
        comms_expiring = Communication.objects.filter(
            communication_par_record__expiry_date__range=[today, one_month_from_now]
        ).distinct()

        for comm in comms_expiring:
            pars = comm.communication_par_record.filter(expiry_date__range=[today, one_month_from_now])
            for par in pars:
                expiring_notifications.append(
                    {
                        "asset_name": f"Comms: {comm.type}",
                        "serial_number": comm.imei_serial or "N/A",
                        "expiry_date": par.expiry_date.strftime("%b %d, %Y"),
                    }
                )
    except Exception as e:
        print("NOTIF COMMUNICATIONS ERROR:", e)

    # ── D. Firearms Expirations ──
    try:
        firearms_expiring = Firearm.objects.filter(
            firearms_par_records__expiry_date__range=[today, one_month_from_now]
        ).distinct()

        for firearm in firearms_expiring:
            pars = firearm.firearms_par_records.filter(expiry_date__range=[today, one_month_from_now])
            for par in pars:
                expiring_notifications.append(
                    {
                        "asset_name": f"Firearm: {firearm.type}",
                        "serial_number": getattr(firearm, "faid_serial", "N/A"),
                        "expiry_date": par.expiry_date.strftime("%b %d, %Y"),
                    }
                )
    except Exception as e:
        print("NOTIF FIREARMS ERROR:", e)

    # Sort Expiry Alerts Chronologically
    try:
        expiring_notifications.sort(
            key=lambda x: timezone.datetime.strptime(x["expiry_date"], "%b %d, %Y")
        )
    except Exception as e:
        print("NOTIF SORT ERROR:", e)

    # Unread count for Logins / Session tracking widget
    unread_activities_badge = sum(1 for a in recent_activities if a["unread"])
    
    # Unread count for Assets Status Changes tracking widget
    unread_assets_badge = sum(1 for a in asset_activities if a["unread"])
    
    # Unread count for active PAR alerts (total expiring items within 1 month)
    unread_notifications_badge = len(expiring_notifications)

    context = {
        # CHANGE THIS LINE HERE: Calculate count dynamically using visible_v
        "total_assets": total_asset.count() + visible_v.count(),
        
        "total_firearms": firearms_all,
        "total_mobility": visible_v.count(),
        "total_communications": comms_all,
        "total_investigative": inves_all.count(),
        "total_ber": total_ber,
        "recent_activities": recent_activities,
        "asset_activities": asset_activities,
        "expiring_notifications": expiring_notifications,
        "current_user_role": current_user_role,
        "recent_badge_count": unread_activities_badge,
        "asset_badge_count": unread_assets_badge,
        "notif_badge_count": unread_notifications_badge,
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
@require_POST
def mark_all_read(request):
    """Marks notifications/activities as read via session parameters"""
    recent_ids = list(LogEntry.objects.order_by("-action_time").values_list("id", flat=True)[:35])
    existing = set(request.session.get("read_activity_ids", []))
    existing.update(str(x) for x in recent_ids)
    request.session["read_activity_ids"] = list(existing)
    request.session.modified = True
    return JsonResponse({"status": "ok", "read_count": len(recent_ids)})


@login_required
def recent_activities_api(request):
    date_filter = request.GET.get("date")
    role_filter = request.GET.get("role")

    logs = LogEntry.objects.select_related("user").filter(
        Q(change_message__icontains="logged in") | Q(change_message__icontains="logged out")
    ).order_by("-action_time")[:5]

    if date_filter:
        logs = logs.filter(action_time__date=date_filter)
    if role_filter:
        logs = logs.filter(user__userprofile__role__iexact=role_filter)

    combined_results = []
    for entry in logs:
        u = entry.user
        name = u.get_full_name() or u.username
        role = _role_label(u)
        
        combined_results.append({
            "actor": f"{name} ({role})",
            "action": "logged in" if "in" in entry.change_message.lower() else "logged out",
            "timestamp_raw": entry.action_time,
            "timestamp": entry.action_time.strftime("%b %d, %Y, %I:%M %p"),
        })

    page_number = request.GET.get("page", 1)
    paginator = Paginator(combined_results, 10)
    page_obj = paginator.get_page(page_number)

    return JsonResponse(
        {
            "results": list(page_obj),
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "number": page_obj.number,
            "num_pages": paginator.num_pages,
        }
    )


@login_required
def asset_activities_api(request):
    date_filter = request.GET.get("date")
    role_filter = request.GET.get("role")
    action_filter = request.GET.get("action") 

    combined_results = []

    # ==========================================
    # 1. BASE FRAMEWORK LOGENTRY FALLBACK
    # ==========================================
    try:
        logs = LogEntry.objects.select_related("user", "content_type").exclude(
            Q(change_message__icontains="logged in") | Q(change_message__icontains="logged out")
        ).order_by("-action_time")

        if date_filter:
            logs = logs.filter(action_time__date=date_filter)
        if role_filter:
            logs = logs.filter(user__userprofile__role__iexact=role_filter)
        if action_filter:
            ACTION_FLAG_MAP = {"Added": ADDITION, "Edited/Moved": CHANGE, "Deleted": DELETION}
            if action_filter in ACTION_FLAG_MAP:
                logs = logs.filter(action_flag=ACTION_FLAG_MAP[action_filter])

        ACTION_TEXT_MAP = {ADDITION: "Added", CHANGE: "Edited/Moved", DELETION: "Deleted"}
        for entry in logs:
            u = entry.user
            name = u.get_full_name() or u.username
            role = getattr(u.userprofile, "role", "User") if hasattr(u, "userprofile") else "User"
            action_text = ACTION_TEXT_MAP.get(entry.action_flag, "Modified")
            if "moved" in str(entry.change_message).lower():
                action_text = "Moved"

            combined_results.append({
                "actor": f"{name} ({role})",
                "action": action_text,
                "item": entry.object_repr,
                "timestamp_raw": entry.action_time,
                "timestamp": entry.action_time.strftime("%b %d, %Y, %I:%M %p"),
            })
    except Exception as e:
        print("API CORE LOG ERROR:", e)

    # ==========================================
    # 2. COMMUNICATIONS MODULE CUSTOM LOGS
    # ==========================================
    try:
        comm_logs = CommunicationActivityLog.objects.all().order_by("-created_at")
        if date_filter:
            comm_logs = comm_logs.filter(created_at__date=date_filter)

        for log in comm_logs:
            raw_act = log.action.lower()
            if "create" in raw_act or "add" in raw_act:
                normalized_action = "Added"
            elif "delete" in raw_act or "remove" in raw_act:
                normalized_action = "Deleted"
            else:
                normalized_action = "Edited/Moved"

            if action_filter and action_filter != normalized_action:
                continue

            combined_results.append({
                "actor": "Communications Module",
                "action": normalized_action,
                "item": log.details,
                "timestamp_raw": log.created_at,
                "timestamp": log.created_at.strftime("%b %d, %Y, %I:%M %p"),
            })
    except Exception as e:
        print("API COMMUNICATIONS MODAL LOG ERROR:", e)

    # ==========================================
    # 3. FIREARMS MODULE CUSTOM LOGS
    # ==========================================
    try:
        fa_logs = FirearmActivityLog.objects.all().order_by("-created_at")
        if date_filter:
            fa_logs = fa_logs.filter(created_at__date=date_filter)

        for log in fa_logs:
            raw_act = log.action.lower()
            if "create" in raw_act or "add" in raw_act:
                normalized_action = "Added"
            elif "delete" in raw_act or "remove" in raw_act:
                normalized_action = "Deleted"
            else:
                normalized_action = "Edited/Moved"

            if action_filter and action_filter != normalized_action:
                continue

            combined_results.append({
                "actor": "Firearms Module",
                "action": normalized_action,
                "item": log.details,
                "timestamp_raw": log.created_at,
                "timestamp": log.created_at.strftime("%b %d, %Y, %I:%M %p"),
            })
    except Exception as e:
        print("API FIREARMS MODAL LOG ERROR:", e)

    # ==========================================
    # 4. MOBILITY MODULE CUSTOM LOGS
    # ==========================================
    try:
        v_logs = ActivityLog.objects.all().order_by("-timestamp")
        if date_filter:
            v_logs = v_logs.filter(timestamp__date=date_filter)

        for log in v_logs:
            raw_act = log.action_type.lower()
            if "create" in raw_act or "add" in raw_act:
                normalized_action = "Added"
            elif "delete" in raw_act or "remove" in raw_act:
                normalized_action = "Deleted"
            else:
                normalized_action = "Edited/Moved"

            if action_filter and action_filter != normalized_action:
                continue

            combined_results.append({
                "actor": "Mobility Module",
                "action": normalized_action,
                "item": log.description,
                "timestamp_raw": log.timestamp,
                "timestamp": log.timestamp.strftime("%b %d, %Y, %I:%M %p"),
            })
    except Exception as e:
        print("API MOBILITY MODAL LOG ERROR:", e)

    # ==========================================
    # 5. INVESTIGATIVE EQUIPMENT LOGS
    # ==========================================
    try:
        inves_logs = InvestigativeActivityLog.objects.all().order_by("-created_at")
        if date_filter:
            inves_logs = inves_logs.filter(created_at__date=date_filter)
        
        for log in inves_logs:
            raw_action = log.action.lower()
            if "created" in raw_action:
                normalized_action = "Added"
            elif "deleted" in raw_action:
                normalized_action = "Deleted"
            else:
                normalized_action = "Edited/Moved"

            if action_filter and action_filter != normalized_action:
                continue

            combined_results.append({
                "actor": "Investigative Module",
                "action": normalized_action,
                "item": log.details,
                "timestamp_raw": log.created_at,
                "timestamp": log.created_at.strftime("%b %d, %Y, %I:%M %p"),
            })
    except Exception as e:
        print("API INVESTIGATIVE LOG ERROR:", e)

    # ==========================================
    # 6. DISPOSAL / BER MODULE LOGS
    # ==========================================
    try:
        disp_logs = DisposalActivityLog.objects.select_related('user').all().order_by("-timestamp")
        if date_filter:
            disp_logs = disp_logs.filter(timestamp__date=date_filter)
        if role_filter:
            disp_logs = disp_logs.filter(user__userprofile__role__iexact=role_filter)

        for log in disp_logs:
            if log.action_type == 'REMOVE':
                normalized_action = "Deleted"
            elif log.action_type == 'FLAGGED':
                normalized_action = "Added"
            else:
                normalized_action = "Edited/Moved"

            if action_filter and action_filter != normalized_action:
                continue

            u = log.user
            name = u.get_full_name() or u.username if u else "System"
            role = getattr(u.userprofile, "role", "User") if u and hasattr(u, "userprofile") else "User"

            combined_results.append({
                "actor": f"{name} ({role})",
                "action": normalized_action,
                "item": log.description.replace(" fa-trash-alt", ""),
                "timestamp_raw": log.timestamp,
                "timestamp": log.timestamp.strftime("%b %d, %Y, %I:%M %p"),
            })
    except Exception as e:
        print("API DISPOSAL LOG ERROR:", e)

    # ==========================================
    # UNIFORM SORTING & PAGINATION
    # ==========================================
    combined_results.sort(key=lambda x: x["timestamp_raw"], reverse=True)

    page_number = request.GET.get("page", 1)
    paginator = Paginator(combined_results, 10)
    page_obj = paginator.get_page(page_number)

    return JsonResponse(
        {
            "results": list(page_obj),
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "number": page_obj.number,
            "num_pages": paginator.num_pages,
        }
    )


@login_required
def notifications_api(request):
    today = timezone.now().date()
    one_month_from_now = today + timedelta(days=30)
    category_filter = request.GET.get("category", "").lower()
    all_expiring = []

    # 1. Investigative
    if not category_filter or category_filter == "investigative":
        try:
            for par in InvestigativePARRecord.objects.filter(expiry_date__range=[today, one_month_from_now]).select_related("asset"):
                all_expiring.append({
                    "category": "Investigative",
                    "asset_name": par.asset.model if par.asset else "Investigative Asset",
                    "serial_number": par.asset.serial_no if par.asset else (par.par_number or "N/A"),
                    "expiry_date": par.expiry_date,
                })
        except Exception as e:
            print("API NOTIF INVES ERR:", e)

    # 2. Mobility
    if not category_filter or category_filter == "mobility":
        try:
            for vehicle in Vehicle.objects.filter(par_records__expiry_date__range=[today, one_month_from_now]).distinct():
                for par in vehicle.par_records.filter(expiry_date__range=[today, one_month_from_now]):
                    all_expiring.append({
                        "category": "Mobility",
                        "asset_name": f"Vehicle: {vehicle.make_model}",
                        "serial_number": vehicle.plate_number or vehicle.conduction_number or "N/A",
                        "expiry_date": par.expiry_date,
                    })
        except Exception as e:
            print("API NOTIF MOBILITY ERR:", e)

    # 3. Communications
    if not category_filter or category_filter == "communications":
        try:
            for comm in Communication.objects.filter(communication_par_record__expiry_date__range=[today, one_month_from_now]).distinct():
                for par in comm.communication_par_record.filter(expiry_date__range=[today, one_month_from_now]):
                    all_expiring.append({
                        "category": "Communications",
                        "asset_name": f"Comms: {comm.type}",
                        "serial_number": comm.imei_serial or "N/A",
                        "expiry_date": par.expiry_date,
                    })
        except Exception as e:
            print("API NOTIF COMMS ERR:", e)

    # 4. Firearms
    if not category_filter or category_filter == "firearms":
        try:
            for firearm in Firearm.objects.filter(firearms_par_records__expiry_date__range=[today, one_month_from_now]).distinct():
                for par in firearm.firearms_par_records.filter(expiry_date__range=[today, one_month_from_now]):
                    all_expiring.append({
                        "category": "Firearms",
                        "asset_name": f"Firearm: {firearm.type}",
                        "serial_number": getattr(firearm, "faid_serial", "N/A"),
                        "expiry_date": par.expiry_date,
                    })
        except Exception as e:
            print("API NOTIF FIREARMS ERR:", e)

    all_expiring.sort(key=lambda x: x["expiry_date"])

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