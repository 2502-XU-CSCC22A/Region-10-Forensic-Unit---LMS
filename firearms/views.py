import json
import uuid
import urllib.request as _urllib
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse
from .forms import FirearmsPARForm
from .models import Firearm
from config.models import AssetStatus, Category
from django.contrib.auth.decorators import login_required

SUPABASE_URL = "https://vamjajitzyspdyfxisac.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhbWphaml0enlzcGR5Znhpc2FjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYyNTkwMDUsImV4cCI6MjA5MTgzNTAwNX0.J8xu0H57Cch1lDpvPtWZqOBkKyzBb8tfUpHaZa2Hjfk"  


def log_firearm_activity(firearm_id, action, details, user=None):
    try:
        user_info = f" by {user.get_full_name() or user.username}" if user and user.is_authenticated else ""
        payload = json.dumps({
            "firearm_id": firearm_id,
            "action": action,
            "details": f"{details}{user_info}",
        }).encode()
        req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/firearms_activitylog",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=minimal",
            },         
            method="POST"
        )
        _urllib.urlopen(req)
    except Exception as e:
        print(f"Activity log error: {e}")


def index(request):
    total_firearms = Firearm.objects.count()
    validated_count = Firearm.objects.filter(validated='VALIDATED').count()
    return render(request, 'firearms/firearms_main.html', {
        'validated_par_count': validated_count,
        'total_par': total_firearms,
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
        latest_par = f.par_records.order_by('-created_at').first()
        firearms_data.append({
            'id':          f.id,
            'name':        f.assigned_to,
            'unit':        f.unit,
            'subunit':     f.subunit,
            'station':     f.station,
            'issuingUnit': f.issuing_unit,
            'faid':        f.faid_serial,
            'serialNo':    f.faid_serial,
            'parNumber':   latest_par.par_number if latest_par else 'N/A',
            'makeModel':   f.type,
            'status':      f.status.status_name if f.status else 'Unknown',
            'validated':   f.validated,
        })
    return JsonResponse({'firearms': firearms_data})


@csrf_exempt
def firearm_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status_obj = AssetStatus.objects.get(status_name__iexact=data.get('status'))
            category, _ = Category.objects.get_or_create(category_name='firearms')
            property_no = f"FA-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

            new_firearm = Firearm.objects.create(
                assigned_to=data.get('name'),
                unit=data.get('unit'),
                subunit=data.get('subunit'),
                station=data.get('station'),
                issuing_unit=data.get('issuingUnit'),
                faid_serial=data.get('faid'),
                type=data.get('makeModel'),
                status=status_obj,
                validated=data.get('validated'),
                date_acquired=data.get('dateAcquired', '2026-01-01'),
                property_no=property_no,
                model=data.get('makeModel'),
                category=category,
                serial_no=data.get('faid') or 'N/A',
                quantity=1,
            )

            log_firearm_activity(
                firearm_id=new_firearm.id,
                action="Created",
                details=f"Firearm '{data.get('name')}' added with serial {data.get('faid')}",
                user=request.user
            )

            return JsonResponse({'success': True})

        except AssetStatus.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Status not found in database'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


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
            firearm.serial_no    = data.get('faid') or 'N/A'
            firearm.type         = data.get('makeModel')
            firearm.status       = status_obj
            firearm.validated    = data.get('validated')
            firearm.save()

            log_firearm_activity(
                firearm_id=pk,
                action="Updated",
                details=f"Firearm '{data.get('name')}' updated — status: {data.get('status')}, remarks: {data.get('validated')}",
                user=request.user
            )

            return JsonResponse({'success': True})
        except Firearm.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Firearm not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
def firearm_delete(request, pk):
    if request.method == 'POST':
        try:
            firearm = Firearm.objects.get(pk=pk)
            name   = firearm.assigned_to
            serial = firearm.faid_serial
            firearm.delete()

            log_firearm_activity(
                firearm_id=pk,
                action="Deleted",
                details=f"Firearm '{name}' (serial: {serial}) was deleted",
                user=request.user
            )

            return JsonResponse({'success': True})
        except Firearm.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Firearm not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


def par_management(request):
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
    return render(request, 'firearms/par_management.html', {'pars': pars, 'p_form': form})


@csrf_exempt
def edit_par(request, pk):
    from .models import FirearmPARRecord
    par = FirearmPARRecord.objects.get(pk=pk)

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
    return render(request, 'firearms/edit_par.html', {'form': form, 'record': par})


def delete_par(request, pk):
    from .models import FirearmPARRecord
    FirearmPARRecord.objects.filter(pk=pk).delete()
    return redirect('firearms:par_management')


def api_par_list(request):
    from .models import FirearmPARRecord
    pars = list(FirearmPARRecord.objects.order_by('-created_at').values(
        'id', 'par_number', 'firearm_id', 'issued_to', 'date_issued', 'expiry_date'
    ))
    return JsonResponse({'pars': pars})


def firearms_activitylog(request):
    return render(request, 'firearms/firearms_activitylog.html')


def firearms_activitylog_api(request):
    days = int(request.GET.get('days', 7))
    from datetime import timedelta, timezone as dt_timezone
    since = (timezone.now() - timedelta(days=days)).astimezone(dt_timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    try:
        url = (
            f"{SUPABASE_URL}/rest/v1/firearms_activitylog"
            f"?created_at=gte.{since}"
            f"&order=created_at.desc"
        )
        req = _urllib.Request(url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })
        with _urllib.urlopen(req) as resp:
            data = json.loads(resp.read())
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def firearm_move_to_ber(request, pk):
    if request.method == 'POST':
        try:
            firearm = Firearm.objects.get(pk=pk)
            name   = firearm.assigned_to
            serial = firearm.faid_serial

            ber_status = AssetStatus.objects.get(status_name__iexact='Unserviceable')  
            firearm.status = ber_status
            firearm.save()

            patch_payload = json.dumps({"StatusID": 4}).encode()
            patch_req = _urllib.Request(
                f"{SUPABASE_URL}/rest/v1/config_asset?id=eq.{pk}",
                data=patch_payload,
                headers={
                    "Content-Type": "application/json",
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                    "Prefer": "return=minimal",
                },
                method="PATCH"
            )
            _urllib.urlopen(patch_req)

            log_firearm_activity(
                firearm_id=pk,
                action="Moved to BER",
                details=f"Firearm '{name}' (serial: {serial}) was moved to BER & Disposal",
                user=request.user
            )

            return JsonResponse({'success': True})
        except Firearm.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Firearm not found'})
        except AssetStatus.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'BER status not found in database'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)