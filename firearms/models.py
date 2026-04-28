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

    # New fields for firearms module
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