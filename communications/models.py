from django.db import models
from config.models import Asset, PARRecord, ICSRecord


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
        'config.PARRecord',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_par_assignments"
    )

    ics_assignment = models.ForeignKey(
        ICSRecord,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_ics_assignments"
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

    reference_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    issued_to = models.CharField(max_length=150)

    date_issued = models.DateField()

    expiry_date = models.DateField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "communications_parrecord"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.par_number} - {self.communication.type}"


class CommunicationICSRecord(models.Model):
    communication = models.ForeignKey(
        Communication,
        on_delete=models.CASCADE,
        related_name="communication_ics_records",
        related_query_name="communication_ics_record",
    )

    ics_number = models.CharField(max_length=100)

    reference_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    issued_to = models.CharField(max_length=150)

    date_issued = models.DateField()

    expiry_date = models.DateField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "communications_icsrecord"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ics_number} - {self.communication.type}"
    
class CommunicationActivityLog(models.Model):
    communication = models.ForeignKey(
        Communication,
        on_delete=models.CASCADE
    )

    action = models.TextField()

    old_stock = models.IntegerField(
        null=True,
        blank=True
    )

    new_stock = models.IntegerField(
        null=True,
        blank=True
    )

    details = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "communications_activitylog"
        ordering = ["-created_at"]

    def __str__(self):
        return self.action