from .models import Vehicle
from firearms.models import Firearm
from communications.models import Communication
from InvestigativeEquipment.models import InvestigativeDetails
from disposal.models import DisposalItem

def sidebar_counts(request):
    return {
        'total_mobility': Vehicle.objects.only('id').count(),
        'total_firearms': Firearm.objects.only('id').count(),
        'total_comms': Communication.objects.exclude(status_id__in=[4, 5]).only('id').count(),
        'total_investigative': InvestigativeDetails.objects.only('id').count(),
        'total_disposal': DisposalItem.objects.only('id').count(),

    }
