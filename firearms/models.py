from django.db import models
from config.models import Asset

VALIDATED_CHOICES = [
    ('VALIDATED', 'Validated'),
    ('PENDING',   'Pending'),
]

class Firearm(Asset):
    type         = models.CharField(max_length=100)
    caliber      = models.CharField(max_length=100, blank=True, null=True)
    faid_serial  = models.CharField(max_length=100, null=True, blank=True)
    assigned_to  = models.CharField(max_length=200, blank=True, null=True)
    unit         = models.CharField(max_length=100, blank=True, null=True)
    subunit      = models.CharField(max_length=100, blank=True, null=True)
    station      = models.CharField(max_length=200, blank=True, null=True)
    issuing_unit = models.CharField(max_length=100, blank=True, null=True)
    validated    = models.CharField(
                       max_length=20,
                       choices=VALIDATED_CHOICES,
                       default='PENDING'
                   )

    class Meta:
        db_table = 'Firearm_Details'
        verbose_name = 'Firearm'

    def __str__(self):
        return f"{self.assigned_to} — {self.faid_serial}"


class FirearmPARRecord(models.Model):
    firearm      = models.ForeignKey(Firearm, on_delete=models.SET_NULL, null=True, blank=True, related_name='par_records')
    par_number   = models.CharField(max_length=50)
    fund_cluster = models.CharField(max_length=100, blank=True, null=True)
    reference_no = models.CharField(max_length=50, blank=True, null=True)
    issued_to    = models.CharField(max_length=100)
    date_issued  = models.DateField()
    expiry_date  = models.DateField(blank=True, null=True)
    remarks      = models.TextField(blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'firearms_parrecord'

    def __str__(self):
        return f"{self.par_number} — {self.issued_to}"