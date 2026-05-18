import json
import uuid
import urllib.request as _urllib
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse
from .forms import FirearmsPARForm
from .models import FirearmPARRecord, Firearm
from .models import Firearm
from communications.models import Communication
from InvestigativeEquipment.models import InvestigativeDetails
from disposal.models import DisposalItem
from mobility.models import Vehicle
from config.models import AssetStatus, Category
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

SUPABASE_URL = "https://vamjajitzyspdyfxisac.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhbWphaml0enlzcGR5Znhpc2FjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYyNTkwMDUsImV4cCI6MjA5MTgzNTAwNX0.J8xu0H57Cch1lDpvPtWZqOBkKyzBb8tfUpHaZa2Hjfk"  

def index(request):
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearms_all = Firearm.objects.count()
    
    current_user_role = request.user.userprofile.role
    inves_all = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5]).count()
    total_ber = DisposalItem.objects.filter(asset_ptr__status_id=4).count()
    
    return render(request, 'firearms/firearms_main.html', {
        'total_vehicles': visible_v.count(),
        'total_comms': comms_all,
        'total_firearms': firearms_all,
        'total_inves': inves_all,
        'total_ber': total_ber,
        'current_user_role': current_user_role,
    })

def par_management(request):
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearms_all = Firearm.objects.count()
    
    current_user_role = request.user.userprofile.role
    inves_all = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5]).count()
    total_ber = DisposalItem.objects.filter(asset_ptr__status_id=4).count()
    
    if request.method == 'POST':
        p_form = FirearmsPARForm(request.POST)

        if p_form.is_valid():

            firearm_id = p_form.cleaned_data['firearm']

            firearm = None
            if firearm_id:
                try:
                    firearm = Firearm.objects.get(pk=firearm_id)
                except Firearm.DoesNotExist:
                    firearm = None

            FirearmPARRecord.objects.create(
                firearm=firearm,
                par_number=p_form.cleaned_data['par_number'],
                fund_cluster=p_form.cleaned_data['fund_cluster'],
                reference_no=p_form.cleaned_data['reference_no'],
                issued_to=p_form.cleaned_data['issued_to'],
                date_issued=p_form.cleaned_data['date_issued'],
                expiry_date=p_form.cleaned_data['expiry_date'],
                remarks=p_form.cleaned_data['remarks'],
            )

        par_record = FirearmPARRecord.objects.create(
            firearm=firearm,
            par_number=p_form.cleaned_data['par_number'],
            fund_cluster=p_form.cleaned_data['fund_cluster'],
            reference_no=p_form.cleaned_data['reference_no'],
            issued_to=p_form.cleaned_data['issued_to'],
            date_issued=p_form.cleaned_data['date_issued'],
            expiry_date=p_form.cleaned_data['expiry_date'],
            remarks=p_form.cleaned_data['remarks'],
        )

        if firearm:
            log_firearm_activity(
                firearm_id=firearm.pk,
                action="PAR Added",
                details=f"PAR '{par_record.par_number}' added for firearm '{firearm.assigned_to}'",
                user=request.user
            )

            return redirect('firearms:par_management')

    else:
        p_form = FirearmsPARForm()

    pars = FirearmPARRecord.objects.select_related('firearm').all().order_by('-created_at')

    return render(request, 'firearms/par_management.html', {
        'p_form': p_form,
        'pars': pars,
        'active_page': 'par_management',
        'total_vehicles': visible_v.count(),
        'total_comms': comms_all,
        'total_firearms': firearms_all,
        'total_inves': inves_all,
        'total_ber': total_ber,
        'current_user_role': current_user_role,
    })

def firearm_list(request):
    try:
        
        firearms_url = f"{SUPABASE_URL}/rest/v1/Firearm_Details?select=*"
        firearms_req = _urllib.Request(firearms_url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })

        with _urllib.urlopen(firearms_req) as resp:
            firearms_data = json.loads(resp.read())


        assets_url = f"{SUPABASE_URL}/rest/v1/config_asset?select=id,StatusID"
        assets_req = _urllib.Request(assets_url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })

        with _urllib.urlopen(assets_req) as resp:
            assets_data = json.loads(resp.read())

        status_map = {
            asset["id"]: asset.get("StatusID")
            for asset in assets_data
        }

        transformed = []

        for f in firearms_data:
            asset_id = f.get("asset_ptr_id")
            status_id = status_map.get(asset_id)

            if status_id == 2:
                status_name = "Unserviceable"
            elif status_id == 4:
                status_name = "BER"
            else:
                status_name = "Serviceable"

            transformed.append({
                "id": asset_id,
                "name": f.get("assigned_to"),
                "serialNo": f.get("faid_serial"),
                "faid": f.get("faid_serial"),
                "makeModel": f.get("type"),
                "station": f.get("station"),
                "subunit": f.get("subunit"),
                "issuingUnit": f.get("issuing_unit"),
                "status": status_name,
                "validated": f.get("validated", "VALIDATED"),
            })

        return JsonResponse({"firearms": transformed})

    except Exception as e:
        print(f"[ERROR] firearm_list: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({"firearms": []}, status=500)
    

@csrf_exempt
def firearm_create(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)

        name = data.get('name') or 'N/A'
        subunit = data.get('subunit') or ''
        station = data.get('station') or ''
        issuing_unit = data.get('issuingUnit') or 'PNP FG'
        faid = data.get('faid') or f"SFA{uuid.uuid4().hex[:6].upper()}"
        make_model = data.get('makeModel') or 'N/A'
        validated = data.get('validated') or 'VALIDATED'


        asset_payload = json.dumps({
            "date_acquired": timezone.now().date().isoformat(),
            "property_no": f"PN-{uuid.uuid4().hex[:10].upper()}",
            "serial_no": faid,
            "model": make_model,
            "quantity": 1,
            "Office": station,
            "StatusID": 1,
            "category_id": 2,
        }).encode()

        asset_req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/config_asset",
            data=asset_payload,
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=representation",
            },
            method="POST"
        )

        with _urllib.urlopen(asset_req) as resp:
            asset_result = json.loads(resp.read())

        asset_id = asset_result[0]["id"]


        firearm_payload = json.dumps({
            "asset_ptr_id": asset_id,
            "type": make_model,
            "caliber": "",
            "faid_serial": faid,
            "assigned_to": name,
            "unit": "",
            "subunit": subunit,
            "station": station,
            "issuing_unit": issuing_unit,
            "validated": validated,
        }).encode()

        firearm_req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/Firearm_Details",
            data=firearm_payload,
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=representation",
            },
            method="POST"
        )

        with _urllib.urlopen(firearm_req) as resp:
            firearm_result = json.loads(resp.read())

        log_firearm_activity(
            firearm_id=asset_id,
            action="Created",
            details=f"Firearm '{name}' added with serial {faid}",
            user=request.user
        )

        return JsonResponse({
            'success': True,
            'message': 'Firearm created successfully',
            'firearm': firearm_result[0] if firearm_result else None,
        })

    except Exception as e:
        print(f'[ERROR] firearm_create: {str(e)}')

        if hasattr(e, 'read'):
            try:
                print(e.read().decode())
            except:
                pass

        import traceback
        traceback.print_exc()

        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

@csrf_exempt
def firearm_update(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)

        status_text = data.get('status', 'Serviceable')
        status_id = 2 if status_text.lower() == 'unserviceable' else 1


        asset_payload = json.dumps({
            "StatusID": status_id,
            "serial_no": data.get('faid') or '',
            "model": data.get('makeModel') or '',
            "Office": data.get('station') or '',
        }).encode()

        asset_req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/config_asset?id=eq.{pk}",
            data=asset_payload,
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=minimal",
            },
            method="PATCH"
        )
        _urllib.urlopen(asset_req)


        firearm_payload = json.dumps({
            "assigned_to": data.get('name') or '',
            "subunit": data.get('subunit') or '',
            "station": data.get('station') or '',
            "issuing_unit": data.get('issuingUnit') or '',
            "faid_serial": data.get('faid') or '',
            "type": data.get('makeModel') or '',
            "validated": data.get('validated') or 'VALIDATED',
        }).encode()

        firearm_req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/Firearm_Details?asset_ptr_id=eq.{pk}",
            data=firearm_payload,
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=minimal",
            },
            method="PATCH"
        )
        _urllib.urlopen(firearm_req)


        log_firearm_activity(
            firearm_id=pk,
                action="Edited",
                details=f"Firearm '{data.get('name')}' record was updated",
                user=request.user
            )

        if status_text.lower() == 'unserviceable':
            log_firearm_activity(
                firearm_id=pk,
                action="Status Changed",
                details=f"Firearm '{data.get('name')}' marked as Unserviceable",
                user=request.user
            )
        elif status_text.lower() == 'serviceable':
            log_firearm_activity(
                firearm_id=pk,
                action="Status Changed",
                details=f"Firearm '{data.get('name')}' marked as Serviceable",
                user=request.user
            )

        return JsonResponse({'success': True, 'message': 'Firearm updated successfully'})

    except Exception as e:
        print(f'[ERROR] firearm_update: {str(e)}')
        if hasattr(e, 'read'):
            try:
                print(e.read().decode())
            except:
                pass
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

def firearm_delete(request, pk):
    return JsonResponse({'success': True, 'message': f'Delete {pk} - implement me'})

def print_par(request, pk):
    par = get_object_or_404(FirearmPARRecord, pk=pk)

    return render(request, 'firearms/print_par.html', {
        'par': par
    })

def edit_par(request, pk):
    record = get_object_or_404(FirearmPARRecord, pk=pk)

    if request.method == 'POST':
        form = FirearmsPARForm(request.POST)

        if form.is_valid():
            firearm_id = form.cleaned_data['firearm']

            firearm = None
            if firearm_id:
                firearm = Firearm.objects.filter(pk=firearm_id).first()

            record.firearm = firearm
            record.par_number = form.cleaned_data['par_number']
            record.fund_cluster = form.cleaned_data['fund_cluster']
            record.reference_no = form.cleaned_data['reference_no']
            record.issued_to = form.cleaned_data['issued_to']
            record.date_issued = form.cleaned_data['date_issued']
            record.expiry_date = form.cleaned_data['expiry_date']
            record.remarks = form.cleaned_data['remarks']
            record.save()

            return redirect('firearms:par_management')

    else:
        form = FirearmsPARForm(initial={
            'par_number': record.par_number,
            'fund_cluster': record.fund_cluster,
            'firearm': record.firearm_id,
            'reference_no': record.reference_no,
            'issued_to': record.issued_to,
            'date_issued': record.date_issued,
            'expiry_date': record.expiry_date,
            'remarks': record.remarks,
        })

    return render(request, 'firearms/edit_par.html', {
        'form': form,
        'record': record,
        'active_page': 'par_management',
    })

def delete_par(request, pk):
    record = get_object_or_404(FirearmPARRecord, pk=pk)

    firearm_id = record.firearm_id
    par_number = record.par_number

    record.delete()

    if firearm_id:
        log_firearm_activity(
            firearm_id=firearm_id,
            action="PAR Deleted",
            details=f"PAR '{par_number}' was deleted",
            user=request.user
        )

    return redirect('firearms:par_management')


def api_par_list(request):
    try:
        url = f"{SUPABASE_URL}/rest/v1/firearms_parrecord?select=*"
        print(f"[DEBUG] api_par_list querying: {url}")
        
        req = _urllib.Request(url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })
        
        with _urllib.urlopen(req) as resp:
            par_data = json.loads(resp.read())
        
        print(f"[DEBUG] Got {len(par_data)} PAR records")
        return JsonResponse({'pars': par_data})
    
    except Exception as e:
        print(f'[ERROR] api_par_list: {str(e)}')
        import traceback
        traceback.print_exc()
        return JsonResponse({'pars': []}, status=500)

def api_par_stats(request):
    try:
        url = f"{SUPABASE_URL}/rest/v1/firearms_parrecord?select=*"
        req = _urllib.Request(url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })
        with _urllib.urlopen(req) as resp:
            par_records = json.loads(resp.read())
        return JsonResponse({'pars': par_records})
    except Exception as e:
        return JsonResponse({'pars': [], 'error': str(e)}, status=500)

def firearms_activitylog(request):
    all_v = Vehicle.objects.all()
    visible_v = all_v.exclude(status__in=['BER', 'Disposed'])
    comms_all = Communication.objects.exclude(status_id__in=[4, 5]).count()
    firearms_all = Firearm.objects.count()
    
    current_user_role = request.user.userprofile.role
    inves_all = InvestigativeDetails.objects.exclude(asset_id__status_id__in=[4, 5]).count()
    total_ber = DisposalItem.objects.filter(asset_ptr__status_id=4).count()

    
    return render(request, 'firearms/firearms_activitylog.html', {
        'total_vehicles': visible_v.count(),
        'total_comms': comms_all,
        'total_firearms': firearms_all,
        'total_inves': inves_all,
        'total_ber': total_ber,
        'current_user_role': current_user_role,
    })

def firearms_activitylog_api(request):
    try:
        url = f"{SUPABASE_URL}/rest/v1/firearms_activitylog?select=*&order=created_at.desc"
        
        print(f"[DEBUG] Activity logs URL: {url}")
        
        req = _urllib.Request(url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })
        
        with _urllib.urlopen(req) as resp:
            response_data = resp.read()
            print(f"[DEBUG] Response length: {len(response_data)}")
            logs = json.loads(response_data)
        
        print(f"[DEBUG] Got {len(logs)} activity logs")
        return JsonResponse(logs, safe=False)
    
    except Exception as e:
        print(f'[ERROR] firearms_activitylog_api: {str(e)}')
        import traceback
        traceback.print_exc()
        return JsonResponse([], safe=False, status=500)

def firearm_move_to_ber(request, pk):
    return firearm_move_to_ber_enhanced(request, pk)



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
 
 
@csrf_exempt
def check_disposal(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        firearm_id = data.get('firearm_id')
        
        if not firearm_id:
            return JsonResponse({'success': False, 'error': 'firearm_id required'}, status=400)
        
        
        url = f"{SUPABASE_URL}/rest/v1/disposal_disposalitems?asset_ptr_id=eq.{firearm_id}&select=id"
        print(f"[DEBUG] check_disposal URL: {url}")
        
        req = _urllib.Request(url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })
        
        with _urllib.urlopen(req) as resp:
            existing = json.loads(resp.read())
        
        exists = len(existing) > 0
        print(f"[DEBUG] check_disposal result: exists={exists}")
        
        return JsonResponse({'success': True, 'exists': exists})
    
    except Exception as e:
        print(f'[ERROR] check_disposal error: {str(e)}')
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def create_disposal(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)
    
    try:
        data = json.loads(request.body)
        firearm_id = data.get('firearm_id')
        
        if not firearm_id:
            return JsonResponse({'success': False, 'error': 'firearm_id required'}, status=400)
        
        
        disposal_payload = {
            'asset_ptr_id': firearm_id,
            'disposal_reason': data.get('disposal_reason', 'Marked as BER from Firearms'),
            'expiry_date': data.get('expiry_date'),
            'disposal_date': data.get('disposal_date'),
            'days_overdue': data.get('days_overdue', 0),
            'processed_by': data.get('processed_by'),
            'personnel_assigned': data.get('personnel_assigned'),
            'last_sync': data.get('last_sync'),
        }
        
        payload = json.dumps(disposal_payload).encode()
        req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/disposal_disposalitems",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=representation",
            },
            method="POST"
        )
        
        with _urllib.urlopen(req) as resp:
            result = json.loads(resp.read())
        
        disposal_id = result[0]['id'] if result else None
        
        return JsonResponse({
            'success': True,
            'message': 'Disposal record created',
            'disposal_id': disposal_id
        })
    
    except Exception as e:
        print(f'[ERROR] create_disposal error: {str(e)}')
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
 

@csrf_exempt
def firearm_move_to_ber_enhanced(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

    try:
        now = timezone.now().isoformat()


        get_url = f"{SUPABASE_URL}/rest/v1/Firearm_Details?asset_ptr_id=eq.{pk}&select=*"
        get_req = _urllib.Request(get_url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })

        with _urllib.urlopen(get_req) as resp:
            firearm_data = json.loads(resp.read())

        if not firearm_data:
            return JsonResponse({'success': False, 'error': 'Firearm not found'}, status=404)

        firearm = firearm_data[0]


        check_url = f"{SUPABASE_URL}/rest/v1/disposal_disposalitems?asset_ptr_id=eq.{pk}&select=asset_ptr_id"
        check_req = _urllib.Request(check_url, headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        })

        with _urllib.urlopen(check_req) as resp:
            existing_disposal = json.loads(resp.read())


        if not existing_disposal:
            disposal_payload = json.dumps({
                "asset_ptr_id": pk,
                "days_overdue": 0,
                "expiry_date": timezone.now().date().isoformat(),
                "disposal_reason": "Marked as BER from Firearms",
                "disposal_date": now,
                "processed_by": None,
                "personnel_assigned": None,
                "last_sync": now,
            }).encode()

            disposal_req = _urllib.Request(
                f"{SUPABASE_URL}/rest/v1/disposal_disposalitems",
                data=disposal_payload,
                headers={
                    "Content-Type": "application/json",
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                    "Prefer": "return=minimal",
                },
                method="POST"
            )
            _urllib.urlopen(disposal_req)


        asset_payload = json.dumps({
            "StatusID": 4,
        }).encode()

        asset_req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/config_asset?id=eq.{pk}",
            data=asset_payload,
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=minimal",
            },
            method="PATCH"
        )
        _urllib.urlopen(asset_req)


        par_delete_req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/firearms_parrecord?firearm_id=eq.{pk}",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=representation",
            },
            method="DELETE"
        )

        with _urllib.urlopen(par_delete_req) as resp:
            deleted_par = json.loads(resp.read() or b"[]")


        details = f"Firearm '{firearm.get('assigned_to')}' moved to BER"

        if deleted_par:
            details += ", and PAR Record is deleted"

        log_firearm_activity(
            firearm_id=pk,
            action="Moved to BER",
            details=details,
            user=None
        )


        delete_req = _urllib.Request(
            f"{SUPABASE_URL}/rest/v1/Firearm_Details?asset_ptr_id=eq.{pk}",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Prefer": "return=representation",
            },
            method="DELETE"
        )

        with _urllib.urlopen(delete_req) as resp:
            deleted_firearm = json.loads(resp.read() or b"[]")

        if not deleted_firearm:
            return JsonResponse({
                'success': False,
                'error': 'No firearm row was deleted. Check RLS DELETE policy for Firearm_Details.'
            }, status=400)

        return JsonResponse({
            'success': True,
            'message': 'Firearm moved to BER successfully'
        })

    except Exception as e:
        print(f'[ERROR] firearm_move_to_ber_enhanced: {str(e)}')

        if hasattr(e, 'read'):
            try:
                print(e.read().decode())
            except:
                pass

        import traceback
        traceback.print_exc()

        return JsonResponse({'success': False, 'error': str(e)}, status=500)