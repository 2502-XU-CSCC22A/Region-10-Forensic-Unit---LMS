from django.db import models
# Import both Asset and PAR from your config app
from config.models import Asset, PARRecord

class Communication(Asset):
    type = models.CharField(max_length=100)
    imei_serial = models.CharField(max_length=100, null=True, blank=True)
    frequency_range = models.CharField(max_length=100)
    stock_level = models.IntegerField(default=0)
    
    # Links to the PAR model already existing in your config app
    par_assignment = models.ForeignKey(
        PARRecord, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='communications'
    )