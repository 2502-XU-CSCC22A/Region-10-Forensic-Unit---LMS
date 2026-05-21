from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from config.models import Asset
from disposal.models import DisposalItem
from mobility.models import Vehicle
from firearms.models import Firearm
from InvestigativeEquipment.models import InvestigativeDetails
from communications.models import Communication

User = get_user_model()


def _role_label(user):
    try:
        return user.userprofile.role
    except Exception:
        return "User"


@login_required
def dashboard_view(request):
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

    log_entries = (
        LogEntry.objects.select_related("user", "content_type")
        .order_by("-action_time")[:20]
    )

    ACTION_FLAG_MAP = {
        ADDITION: "added record",
        CHANGE: "updated record",
        DELETION: "removed record",
    }

    read_ids = set(request.session.get("read_activity_ids", []))
    activities = []

    for entry in log_entries:
        u = entry.user
        name = u.get_full_name() or u.username
        role = _role_label(u)
        actor = f"{name} ({role})"

        change_message = str(entry.change_message or "")

        if "logged in" in change_message.lower():
            action_text = change_message
            item_text = ""
            is_login = True
        else:
            action_text = ACTION_FLAG_MAP.get(entry.action_flag, "modified record")
            item_text = entry.object_repr
            is_login = False

        initials = (
            "".join(p[0].upper() for p in name.split()[:2])
            or u.username[0].upper()
        )

        activities.append(
            {
                "id": entry.id,
                "initials": initials,
                "actor": actor,
                "action": action_text,
                "item": item_text,
                "timestamp": entry.action_time.strftime("%b %d, %Y"),
                "unread": entry.id not in read_ids,
                "is_login": is_login,
            }
        )

    unread_count = sum(1 for a in activities if a["unread"])

    context = {
        "total_assets": total_asset.count(),
        "total_firearms": firearms_all,
        "total_mobility": visible_v.count(),
        "total_communications": comms_all,
        "total_investigative": inves_all.count(),
        "total_ber": total_ber,
        "activities": activities,
        "current_user_role": current_user_role,
        "notification_count": unread_count,
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
@require_POST
def mark_all_read(request):
    recent_ids = list(
        LogEntry.objects.order_by("-action_time").values_list("id", flat=True)[:20]
    )

    existing = set(request.session.get("read_activity_ids", []))
    existing.update(recent_ids)

    request.session["read_activity_ids"] = list(existing)
    request.session.modified = True

    return JsonResponse({"status": "ok", "read_count": len(recent_ids)})