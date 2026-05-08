import json
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from .forms import FirearmsPARForm
from .models import Firearm
from config.models import AssetStatus, Category
from mobility.models import Vehicle
from communications.models import Communication
from config.models import Asset, AssetStatus, Personnel
from InvestigativeEquipment.models import InvestigativeDetails
from disposal.models import DisposalItem

def index(request):

    total_firearms = Firearm.objects.count()
    validated_count = Firearm.objects.filter(validated='VALIDATED').count()
    current_user_role = request.user.userprofile.role
    
    vehicle_all = Vehicle.objects.count()
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    inves_all = InvestigativeDetails.objects.count()
    total_ber = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
    ).count()
    
    return render(request, 'firearms/firearms_main.html', {
        'validated_par_count': validated_count, 
        'total_par': total_firearms,
        'vehicle_all': vehicle_all,
        'comms_all': comms_all,
        'inves_all': inves_all,
        'total_ber': total_ber,
        'total_firearms': total_firearms,
        'current_user_role': current_user_role,
    })

def print_par(request, pk):

    dummy_par = {
        'pk': pk,
        'par_number': f'PAR-2026-{pk:03d}',
        'firearm': {'make': 'AK47', 'model': 'PERIOD', 'serial_no': 'AGG8', 'faid': 'SFA69696'},
        'issued_to': 'Precious',
        'date_issued': timezone.now(),
    }
    return render(request, 'firearms/print_par.html', {'par': dummy_par})

def firearm_list(request):
    firearms_query = Firearm.objects.all()
    firearms_data = []
    for f in firearms_query:
        firearms_data.append({
            'id': f.id,
            'name': f.assigned_to, 
            'unit': f.unit,
            'subunit': f.subunit,
            'station': f.station,
            'issuingUnit': f.issuing_unit,
            'faid': f.faid_serial,
            'serialNo': f.serial_no,
            'makeModel': f.type,
            'status': f.status.status_name if f.status else "Unknown", 
            'validated': f.validated
        })
    return JsonResponse({'firearms': firearms_data})

@csrf_exempt
def firearm_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            status_obj = AssetStatus.objects.get(status_name=data.get('status'))
            category, _ = Category.objects.get_or_create(category_name='firearms')
            property_no = f"FA-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

            Firearm.objects.create(
                assigned_to=data.get('name'),
                unit=data.get('unit'),
                subunit=data.get('subunit'),
                station=data.get('station'),
                issuing_unit=data.get('issuingUnit'),
                faid_serial=data.get('faid'),
                serial_no=data.get('serialNo'),
                type=data.get('makeModel'),
                status=status_obj,
                validated=data.get('validated'),
                date_acquired=data.get('dateAcquired', '2026-01-01'),
                property_no=property_no,
                model=data.get('makeModel'),
                category=category,
            )
            return JsonResponse({'success': True})

        except AssetStatus.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Status not found in database'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
         
def par_management(request):
    current_user_role = request.user.userprofile.role
    total_firearms = Firearm.objects.count()
    vehicle_all = Vehicle.objects.count()
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    inves_all = InvestigativeDetails.objects.count()
    total_ber = DisposalItem.objects.filter(
        asset_ptr__status_id=4, 
    ).count()
    
    if request.method == 'POST':
        form = FirearmsPARForm(request.POST)
        if form.is_valid():
            from .models import FirearmPARRecord
            FirearmPARRecord.objects.create(
                firearm_id=form.cleaned_data.get('firearm') or None,
                par_number=form.cleaned_data['par_number'],
                fund_cluster=form.cleaned_data.get('fund_cluster'),
                reference_no=form.cleaned_data.get('reference_no'),
                issued_to=form.cleaned_data['issued_to'],
                date_issued=form.cleaned_data['date_issued'],
                expiry_date=form.cleaned_data.get('expiry_date'),
                remarks=form.cleaned_data.get('remarks'),
            )
            return redirect('firearms:par_management')
    else:
        form = FirearmsPARForm()

    from .models import FirearmPARRecord
    pars = FirearmPARRecord.objects.all().order_by('-created_at')

    return render(request, 'firearms/par_management.html', {
        'pars': pars,
        'p_form': form,
        'current_user_role': current_user_role,
        'vehicle_all': vehicle_all,
        'comms_all': comms_all,
        'inves_all': inves_all,
        'total_ber': total_ber,
        'total_firearms': total_firearms,
    })

@csrf_exempt
def firearm_update(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            firearm = Firearm.objects.get(pk=pk)
            status_obj = AssetStatus.objects.get(status_name=data.get('status'))

            firearm.assigned_to  = data.get('name')
            firearm.unit         = data.get('unit')
            firearm.subunit      = data.get('subunit')
            firearm.station      = data.get('station')
            firearm.issuing_unit = data.get('issuingUnit')
            firearm.faid_serial  = data.get('faid')
            firearm.serial_no    = data.get('serialNo')
            firearm.type         = data.get('makeModel')
            firearm.status       = status_obj
            firearm.validated    = data.get('validated')
            firearm.save()

            return JsonResponse({'success': True})
        except Firearm.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Firearm not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
def firearm_delete(request, pk):
    if request.method == 'POST':
        try:
            Firearm.objects.get(pk=pk).delete()
            return JsonResponse({'success': True})
        except Firearm.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Firearm not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

def edit_par(request, pk):
    from .models import FirearmPARRecord
    par = FirearmPARRecord.objects.get(pk=pk)
    
    current_user_role = request.user.userprofile.role

    if request.method == 'POST':
        form = FirearmsPARForm(request.POST)
        if form.is_valid():
            par.par_number   = form.cleaned_data['par_number']
            par.fund_cluster = form.cleaned_data.get('fund_cluster')
            par.reference_no = form.cleaned_data.get('reference_no')
            par.issued_to    = form.cleaned_data['issued_to']
            par.date_issued  = form.cleaned_data['date_issued']
            par.expiry_date  = form.cleaned_data.get('expiry_date')
            par.remarks      = form.cleaned_data.get('remarks')
            par.firearm_id   = form.cleaned_data.get('firearm') or None
            par.save()
            return redirect('firearms:par_management')
    else:
        form = FirearmsPARForm(initial={
            'par_number':   par.par_number,
            'fund_cluster': par.fund_cluster,
            'reference_no': par.reference_no,
            'issued_to':    par.issued_to,
            'date_issued':  par.date_issued,
            'expiry_date':  par.expiry_date,
            'remarks':      par.remarks,
            'firearm':      par.firearm_id,
        })

    return render(request, 'firearms/edit_par.html', {
        'form': form,
        'record': par, 
        'current_user_role': current_user_role,
    })


def delete_par(request, pk):
    from .models import FirearmPARRecord
    FirearmPARRecord.objects.filter(pk=pk).delete()
    return redirect('firearms:par_management')

def api_par_list(request):
    from .models import FirearmPARRecord
    pars = list(FirearmPARRecord.objects.values(
        'id', 'par_number', 'issued_to', 'date_issued', 'expiry_date'
    ))
    return JsonResponse({'pars': pars})