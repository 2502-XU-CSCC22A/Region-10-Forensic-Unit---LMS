from django.shortcuts import render
from .models import DisposalItem # Make sure this matches your model name
from django.utils import timezone
from datetime import timedelta
import csv
from django.http import HttpResponse
from .models import DisposalItem


def export_disposal_csv(request):
    # 1. Apply the SAME filters as your list view
    items = DisposalItem.objects.select_related('asset_ptr', 'asset_ptr__category').all()
    
    device_type = request.GET.get('device_type')
    if device_type and device_type != 'all':
        items = items.filter(asset_ptr__category__category_name__iexact=device_type)
    
    # ... add your other filters (expiry, station) here ...

    # 2. Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="disposal_report_{timezone.now().date()}.csv"'

    writer = csv.writer(response)
    # 3. Write the Header Row
    writer.writerow(['Asset Model', 'Serial Number', 'Category', 'Expiry Date', 'Reason'])

    # 4. Write Data Rows
    for item in items:
        writer.writerow([
            item.asset_ptr.model,
            item.asset_ptr.serial_no,
            item.asset_ptr.category.category_name,
            item.expiry_date,
            item.disposal_reason
        ])

    return response

def disposal_list(request):
    # 'asset_ptr' is the field Django uses to link DisposalItem to Asset
    # 'category' is the field on Asset that links to Category
    items = DisposalItem.objects.select_related('asset_ptr', 'asset_ptr__category').all()

    device_type = request.GET.get('device_type')
    expiry_status = request.GET.get('expiry_status')

    # Filtering logic
    if device_type and device_type != 'all':
        # Path: asset_ptr -> category -> category_name
        # Use __iexact to handle case-matching automatically
        items = items.filter(asset_ptr__category__category_name__iexact=device_type)

    if expiry_status == 'Expired':
        # Match your database column name: 'expiry_date'
        items = items.filter(expiry_date__lt=timezone.now())
        
    elif expiry_status == 'Expired_3Months':
        today = timezone.now()
        three_months_later = today + timedelta(days=90)
        items = items.filter(expiry_date__range=(today, three_months_later))

    return render(request, 'disposal/disposal_admin.html', {'items': items})