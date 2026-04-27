import uuid
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import connection
from .models import Firearm
from config.models import Asset, AssetStatus, Category
 
 
def index(request):
    return render(request, 'firearms/firearms_main.html', {
        'active_page': 'firearms',
    })
 
 
@require_http_methods(['GET'])
def firearm_list(request):
    firearms = Firearm.objects.all()
    return JsonResponse({'firearms': [_serialize(f) for f in firearms]})

 
@csrf_exempt
@require_http_methods(['POST'])
def firearm_create(request):
    try:
        body = json.loads(request.body)
 
        category, _ = Category.objects.get_or_create(category_name='Firearm')

        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT "StatusID" FROM "Asset_Status" WHERE "Status_Name" = %s LIMIT 1',
                [body.get('status', 'Serviceable')]
            )
            row = cursor.fetchone()
            status_id = row[0] if row else 6

 #      status_name = body.get('status', 'SERVICEABLE')
 #      status_obj, _ = AssetStatus.objects.get_or_create(status_name=status_name)
 
        uid          = str(uuid.uuid4())[:8]
        serial_no    = body.get('serialNo') or f"SN-{uid}"
        property_no  = f"PROP-{uid}"
 
        firearm = Firearm.objects.create(
      
            property_no   = property_no,
            serial_no     = serial_no,
            model         = body.get('makeModel', ''),
            date_acquired = timezone.now().date(),
            category      = category,
#           status        = status_obj,
            status_id     = status_id,
 
            type          = body.get('makeModel', ''),
            caliber       = body.get('makeModel', ''),
            faid_serial   = body.get('faid', ''),
            assigned_to   = body.get('name', ''),
            unit          = body.get('unit', ''),
            subunit       = body.get('subunit', ''),
            station       = body.get('station', ''),
            issuing_unit  = body.get('issuingUnit', ''),
            validated     = body.get('validated', 'PENDING'),
        )
        return JsonResponse({'success': True, 'firearm': _serialize(firearm)}, status=201)
 
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
 
 
@csrf_exempt
@require_http_methods(['POST'])
def firearm_update(request, pk):
    try:
        firearm = Firearm.objects.get(pk=pk)
        body    = json.loads(request.body)

        if 'status' in body:
            with connection.cursor() as cursor:
                cursor.execute(
                'SELECT "StatusID" FROM "Asset_Status" WHERE "Status_Name" = %s LIMIT 1',
                [body['status']]
                )
                row = cursor.fetchone()
                if row:
                    firearm.status_id = row[0]

        if 'serialNo'    in body: firearm.serial_no    = body['serialNo']
        if 'makeModel'   in body:
            firearm.model = body['makeModel']
            firearm.type  = body['makeModel']
        if 'faid'        in body: firearm.faid_serial  = body['faid']
        if 'name'        in body: firearm.assigned_to  = body['name']
        if 'unit'        in body: firearm.unit         = body['unit']
        if 'subunit'     in body: firearm.subunit      = body['subunit']
        if 'station'     in body: firearm.station      = body['station']
        if 'issuingUnit' in body: firearm.issuing_unit = body['issuingUnit']
        if 'validated'   in body: firearm.validated    = body['validated']
 
        firearm.save()
        return JsonResponse({'success': True, 'firearm': _serialize(firearm)})
 
    except Firearm.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
 
 
@csrf_exempt
@require_http_methods(['POST'])
def firearm_delete(request, pk):
    try:
        Firearm.objects.get(pk=pk).delete()
        return JsonResponse({'success': True})
    except Firearm.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
 
 
def _serialize(f):
    status_name = 'SERVICEABLE'

    if f.status_id:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT "Status_Name" FROM "Asset_Status" WHERE "StatusID" = %s LIMIT 1',
                    [f.status_id]
                )
                row = cursor.fetchone()
                if row:
                    status_name = row[0]
                    
        except Exception:
            status_name = 'SERVICEABLE'

    return {
        'id':          f.pk,
        'name':        f.assigned_to  or 'N/A',
        'unit':        f.unit         or 'N/A',
        'subunit':     f.subunit      or 'N/A',
        'station':     f.station      or 'N/A',
        'issuingUnit': f.issuing_unit or 'N/A',
        'faid':        f.faid_serial  or 'N/A',
        'serialNo':    f.serial_no    or 'N/A',
        'makeModel':   f.model        or 'N/A',
        'status':      status_name.upper(),
        'validated':   f.validated    or 'PENDING',
    }