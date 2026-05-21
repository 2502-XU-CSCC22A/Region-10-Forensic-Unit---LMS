from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from config.models import Asset, AssetStatus, Category
from disposal.models import DisposalItem
from mobility.models import Vehicle
from firearms.models import Firearm
from InvestigativeEquipment.models import InvestigativeDetails
from communications.models import Communication

User = get_user_model()


def _role_label(user):
    """Read the role varchar column directly from auth_user."""
    return getattr(user, "role", None) or (
        "Admin" if (user.is_superuser or user.is_staff) else "User"
    )


@login_required
def dashboard_view(request):
    def count_category(name):
        return Asset.objects.filter(category__category_name__iexact=name).count()

    def count_status(name):
        return Asset.objects.filter(status__status_name__iexact=name).count()

    total_asset = Asset.objects.exclude(status__in=[4, 5])
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearms_all = Firearm.objects.count()
    inves_all = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5])
    
    total_ber = DisposalItem.objects.filter(asset_ptr__status_id=4).count()
    current_user_role = request.user.userprofile.role

    from django.contrib.contenttypes.models import ContentType

    asset_ct = ContentType.objects.get_for_model(Asset)

    log_entries = (
        LogEntry.objects.filter(content_type=asset_ct)
        .select_related("user")
        .order_by("-action_time")
    )

    ACTION_FLAG_MAP = {
        ADDITION: "added asset",
        CHANGE: "updated asset",
        DELETION: "removed asset",
    }

    read_ids = set(request.session.get("read_activity_ids", []))

    activities = []

    if log_entries.exists():
        for entry in log_entries:
            u = entry.user
            role = _role_label(u)
            name = u.get_full_name() or u.username
            actor = f"{name} ({role})"

            action_text = ACTION_FLAG_MAP.get(entry.action_flag, "modified asset")
            initials = (
                "".join(p[0].upper() for p in name.split()[:2]) or u.username[0].upper()
            )

            activities.append(
                {
                    "id": entry.id,
                    "initials": initials,
                    "actor": actor,
                    "action": action_text,
                    "item": entry.object_repr,
                    "timestamp": entry.action_time.strftime("%b %d, %Y %I:%M %p"),
                    "unread": entry.id not in read_ids,
                }
            )
    else:
        recent_assets = Asset.objects.select_related("status", "category").order_by(
            "-id"
        )
        current_user = request.user
        current_role = _role_label(current_user)
        current_name = current_user.get_full_name() or current_user.username
        current_actor = f"{current_name} ({current_role})"
        current_initials = (
            "".join(p[0].upper() for p in current_name.split()[:2])
            or current_user.username[0].upper()
        )

        for asset in recent_assets:
            activities.append(
                {
                    "id": asset.id,
                    "initials": current_initials,
                    "actor": current_actor,
                    "action": "recorded asset",
                    "item": f"{asset.category.category_name} – {asset.property_no}",
                    "timestamp": asset.date_acquired.strftime("%b %d, %Y") if asset.date_acquired else "N/A",
                    "unread": asset.id not in read_ids,
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
    from django.contrib.contenttypes.models import ContentType

    asset_ct = ContentType.objects.get_for_model(Asset)
    recent_ids = list(
        LogEntry.objects.filter(content_type=asset_ct)
        .order_by("-action_time")
        .values_list("id", flat=True)
    )
    if not recent_ids:
        recent_ids = list(Asset.objects.order_by("-id").values_list("id", flat=True))

    existing = set(request.session.get("read_activity_ids", []))
    existing.update(recent_ids)
    request.session["read_activity_ids"] = list(existing)
    request.session.modified = True
    return JsonResponse({"status": "ok", "read_count": len(recent_ids)})
