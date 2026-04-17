from django.db import models

class DisposalItem(models.Model):
    unit = models.CharField(max_length=100)
    sub_unit = models.CharField(max_length=100)
    comm_type = models.CharField(max_length=100) # You can store "Fantasy, Fiction" here
    expiry_status = models.DateField()
    station_url = models.URLField()

    def __str__(self):
        return self.sub_unit