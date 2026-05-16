from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehicle, PARRecord, ActivityLog
from .forms import VehicleForm
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
import smtplib
import ssl
from django.conf import settings
from disposal.models import DisposalItem
from firearms.models import Firearm
from communications.models import Communication
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

# Added: use develop config/models.py without changing it
from config.models import Asset, AssetStatus, Category


def can_edit(user):
    try:
        role = user.userprofile.role
        return role in ['Admin', 'Logistics Officer']
    except Exception:
        return False


def create_vehicle_asset(vehicle, request):
    """
    Creates an Asset record required by the develop branch config/models.py.
    Do not change config/models.py; supply the required fields here instead.
    """

    status_name = getattr(vehicle, 'status', None) or 'Serviceable'

    try:
        asset_status = AssetStatus.objects.get(status_name=status_name)
    except AssetStatus.DoesNotExist:
        asset_status = AssetStatus.objects.get(status_name='Serviceable')

    category, _ = Category.objects.get_or_create(category_name='Vehicle')

    property_no = (
        request.POST.get('property_no')
        or getattr(vehicle, 'property_no', None)
        or f"MOB-{getattr(vehicle, 'plate_number', '') or getattr(vehicle, 'conduction_number', '') or timezone.now().strftime('%Y%m%d%H%M%S')}"
    )

    serial_no = (
        getattr(vehicle, 'chassis_number', None)
        or getattr(vehicle, 'engine_number', None)
        or getattr(vehicle, 'conduction_number', None)
        or getattr(vehicle, 'plate_number', None)
        or property_no
    )

    asset = Asset.objects.create(
        date_acquired=request.POST.get('date_acquired') or timezone.now().date(),
        property_no=property_no,
        serial_no=serial_no,
        model=getattr(vehicle, 'make_model', None) or 'Vehicle',
        quantity='1',
        status=asset_status,
        category=category,
        office='Mobility'
    )

    return asset


@login_required
def vehicle_management(request):
    query = Q()
    search = request.GET.get('plate_no')

    if search:
        query &= (
            Q(vehicle_id__icontains=search) |
            Q(plate_number__icontains=search) |
            Q(conduction_number__icontains=search) |
            Q(make_model__icontains=search) |
            Q(classification__icontains=search) |
            Q(primary_driver__icontains=search) |
            Q(alternative_driver__icontains=search)
        )

    all_d = DisposalItem.objects.filter(category_id__in=[3, 10])
    all_c = Communication.objects.exclude(status_id__in=[4, 5])
    all_f = Firearm.objects.all()

    if request.method == 'POST':
        if not can_edit(request.user):
            return HttpResponseForbidden("You do not have permission.")

        form = VehicleForm(request.POST)

        if form.is_valid():
            vehicle = form.save(commit=False)

            asset = create_vehicle_asset(vehicle, request)

            # This works only if your Vehicle model has an asset field.
            # Example: asset = models.ForeignKey(Asset, ...)
            if hasattr(vehicle, 'asset'):
                vehicle.asset = asset

            vehicle.save()

            par_created = False

            par_number = request.POST.get('par_number')
            issued_to = request.POST.get('issued_to')
            date_acquired = request.POST.get('date_acquired')
            expiry_date = request.POST.get('expiry_date')
            remarks = request.POST.get('remarks')

            if par_number and issued_to:
                PARRecord.objects.create(
                    vehicle=vehicle,
                    par_number=par_number,
                    issued_to=issued_to,
                    date_acquired=date_acquired or timezone.now().date(),
                    expiry_date=expiry_date or None,
                    remarks=remarks
                )

                par_created = True

            ActivityLog.objects.create(
                user=request.user,
                action_type='CREATE',
                description=f"Added new vehicle: {vehicle.make_model} ({vehicle.plate_number or vehicle.conduction_number})"
            )

            if vehicle.status == 'BER':
                messages.warning(
                    request,
                    "Vehicle marked as BER, sent to BER & Disposal, and removed from the Mobility table."
                )
            elif par_created:
                messages.success(request, "Vehicle and PAR details added successfully.")
            else:
                messages.success(request, "Vehicle added successfully.")

            return redirect('mobility:vehicle_management')

        else:
            messages.error(request, "Please correct the errors in the vehicle form.")
            messages.error(request, form.errors)

    else:
        form = VehicleForm()

    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])

    today = timezone.now().date()
    upcoming_limit = today + timedelta(days=30)

    context = {
        'form': form,
        'vehicles': visible_v.filter(query).order_by('-id'),
        'can_edit': can_edit(request.user),

        'total_vehicles': visible_v.count(),
        's_count': visible_v.filter(status='Serviceable').count(),
        'validated_par_count': PARRecord.objects.filter(
            expiry_date__gt=upcoming_limit
        ).count(),
        'expiring_count': PARRecord.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=upcoming_limit
        ).count(),

        'total_disposal': all_d.count(),
        'total_firearms': all_f.count(),
        'total_comms': all_c.count(),
    }

    return render(request, 'mobility/vehicle_management.html', context)


@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if vehicle.status == 'Disposed':
        messages.error(request, "Disposed vehicles are locked from editing.")
        return redirect('mobility:vehicle_management')

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)

        if form.is_valid():
            updated_vehicle = form.save()

            # Optional: sync linked Asset status/model if Vehicle has asset
            if hasattr(updated_vehicle, 'asset') and updated_vehicle.asset:
                try:
                    asset_status = AssetStatus.objects.get(status_name=updated_vehicle.status)
                    updated_vehicle.asset.status = asset_status
                    updated_vehicle.asset.model = updated_vehicle.make_model
                    updated_vehicle.asset.save()
                except AssetStatus.DoesNotExist:
                    pass

            ActivityLog.objects.create(
                user=request.user,
                action_type='UPDATE',
                description=f"Updated vehicle: {updated_vehicle.make_model} ({updated_vehicle.plate_number or updated_vehicle.conduction_number})"
            )

            if updated_vehicle.status == 'BER':
                messages.warning(
                    request,
                    "Vehicle marked as BER, sent to BER & Disposal, and removed from the Mobility table."
                )
            else:
                messages.success(request, "Vehicle updated successfully.")

            return redirect('mobility:vehicle_management')

        else:
            messages.error(request, "Please correct the errors before saving.")
            messages.error(request, form.errors)

    return redirect('mobility:vehicle_management')


@login_required
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if vehicle.status == 'Disposed':
        messages.error(request, "Disposed vehicles cannot be deleted.")
        return redirect('mobility:vehicle_management')

    ActivityLog.objects.create(
        user=request.user,
        action_type='DELETE',
        description=f"Deleted vehicle: {vehicle.make_model} ({vehicle.plate_number or vehicle.conduction_number})"
    )

    vehicle.delete()
    messages.warning(request, "Vehicle record deleted.")
    return redirect('mobility:vehicle_management')


@login_required
def mark_vehicle_ber(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if vehicle.status != 'Disposed':
        vehicle.status = 'BER'
        vehicle.save()

        if hasattr(vehicle, 'asset') and vehicle.asset:
            try:
                asset_status = AssetStatus.objects.get(status_name='BER')
                vehicle.asset.status = asset_status
                vehicle.asset.save()
            except AssetStatus.DoesNotExist:
                pass

        ActivityLog.objects.create(
            user=request.user,
            action_type='UPDATE',
            description=f"Marked vehicle as BER: {vehicle.make_model} ({vehicle.plate_number or vehicle.conduction_number})"
        )

        messages.warning(request, "Vehicle marked as BER and reflected in Disposal/BER.")

    return redirect('mobility:vehicle_management')


@login_required
def send_vehicle_to_disposal(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if vehicle.status == 'BER':
        vehicle.status = 'Disposed'
        vehicle.save()

        if hasattr(vehicle, 'asset') and vehicle.asset:
            try:
                asset_status = AssetStatus.objects.get(status_name='Disposed')
                vehicle.asset.status = asset_status
                vehicle.asset.save()
            except AssetStatus.DoesNotExist:
                pass

        ActivityLog.objects.create(
            user=request.user,
            action_type='UPDATE',
            description=f"Vehicle disposed via BER Department: {vehicle.make_model} ({vehicle.plate_number or vehicle.conduction_number})"
        )

        messages.success(request, "Vehicle has been marked as disposed.")

    return redirect('mobility:vehicle_management')


@login_required
def par_management(request):
    today = timezone.now().date()
    upcoming_limit = today + timedelta(days=30)

    search = request.GET.get('search')
    status = request.GET.get('status')

    pars = PARRecord.objects.select_related('vehicle').all()

    if search:
        pars = pars.filter(
            Q(par_number__icontains=search) |
            Q(issued_to__icontains=search) |
            Q(vehicle__vehicle_id__icontains=search) |
            Q(vehicle__plate_number__icontains=search) |
            Q(vehicle__conduction_number__icontains=search) |
            Q(vehicle__make_model__icontains=search)
        )

    if status == 'expiring':
        pars = pars.filter(expiry_date__gte=today, expiry_date__lte=upcoming_limit)
    elif status == 'expired':
        pars = pars.filter(expiry_date__lt=today)
    elif status == 'validated':
        pars = pars.filter(expiry_date__gt=upcoming_limit)

    context = {
        'pars': pars.order_by('-date_acquired'),
        'today': today,
        'upcoming_limit': upcoming_limit,
        'search': search,
        'status': status,
        'can_edit': can_edit(request.user),
    }

    return render(request, 'mobility/par_management.html', context)


@login_required
def delete_par(request, pk):
    par = get_object_or_404(PARRecord, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    ActivityLog.objects.create(
        user=request.user,
        action_type='DELETE',
        description=f"Deleted PAR Record: {par.par_number}"
    )

    par.delete()
    messages.warning(request, "PAR record removed.")
    return redirect('mobility:par_management')


@login_required
def print_par(request, pk):
    par = get_object_or_404(
        PARRecord.objects.select_related('vehicle'),
        pk=pk
    )

    return render(request, 'mobility/print_par.html', {'par': par})


@login_required
def activity_log(request):
    period = request.GET.get('period', 'week')
    days = 7 if period == 'week' else 30
    cutoff = timezone.now() - timedelta(days=days)

    logs = ActivityLog.objects.filter(
        timestamp__gte=cutoff
    ).select_related('user').order_by('-timestamp')

    return render(request, 'mobility/activity_log.html', {
        'logs': logs,
        'period': period
    })


@login_required
def manual_email_alert(request):
    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    urgent = Vehicle.objects.filter(status__in=['Unserviceable', 'BER'])

    if urgent.exists():
        vehicle_list = "\n".join([
            f"- {v.make_model} ({v.plate_number or v.conduction_number}): {v.status}"
            for v in urgent
        ])

        message_body = (
            "Subject: RFU 10 Mobility Alert\n\n"
            "The following vehicles require immediate attention:\n\n"
            f"{vehicle_list}\n\n"
            "Please update the records once action has been taken."
        )

        try:
            context = ssl._create_unverified_context()

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls(context=context)
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(
                    settings.EMAIL_HOST_USER,
                    ['dlpalayen@gmail.com'],
                    message_body
                )

            messages.success(request, "Alert email sent successfully!")

        except Exception as e:
            messages.error(request, f"Email failed: {e}")

    else:
        messages.info(request, "No urgent vehicle records found.")

    return redirect('mobility:vehicle_management')


@login_required
def edit_par(request, pk):
    par = get_object_or_404(PARRecord, pk=pk)

    if not can_edit(request.user):
        return HttpResponseForbidden("You do not have permission.")

    if request.method == 'POST':
        par.par_number = request.POST.get('par_number')
        par.issued_to = request.POST.get('issued_to')
        par.date_acquired = request.POST.get('date_acquired') or None
        par.expiry_date = request.POST.get('expiry_date') or None
        par.remarks = request.POST.get('remarks')

        par.save()

        ActivityLog.objects.create(
            user=request.user,
            action_type='UPDATE',
            description=f"Updated PAR Record: {par.par_number}"
        )

        messages.success(request, "PAR record updated successfully.")
        return redirect('mobility:par_management')

    return redirect('mobility:par_management')