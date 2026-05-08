from django.db import models
from config.models import Asset, PARRecord


class Communication(Asset):
    type = models.CharField(max_length=100)

    imei_serial = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    radio_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    remarks = models.CharField(
        max_length=100,
        default="VALIDATED"
    )

    is_deleted = models.BooleanField(default=False)

    par_assignment = models.ForeignKey(
        PARRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_assignments"
    )

    class Meta:
        db_table = "communications_communication"

    def __str__(self):
        return f"{self.type} - {self.imei_serial}"

class CommunicationPARRecord(models.Model):
    communication = models.ForeignKey(
        Communication,
        on_delete=models.CASCADE,
        related_name="communication_par_records",
        related_query_name="communication_par_record",
    )

    par_number = models.CharField(max_length=100)
    fund_cluster = models.CharField(max_length=100, blank=True, null=True)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    issued_to = models.CharField(max_length=150)
    date_issued = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "communications_parrecord"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.par_number} - {self.communication.type}"