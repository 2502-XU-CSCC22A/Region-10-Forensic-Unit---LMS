from django.db import models
from config.models import Asset # Import the parent table from the Core app

class Communication(Asset): # This 'Asset' link creates the 1:1 relationship
    type = models.CharField(max_length=100)
    imei_serial = models.CharField(max_length=100, null=True, blank=True)
    frequency_range = models.CharField(max_length=100)
    # You can change 'Encryption_Status' to 'Stock_Level' here
    stock_level = models.IntegerField(default=0)