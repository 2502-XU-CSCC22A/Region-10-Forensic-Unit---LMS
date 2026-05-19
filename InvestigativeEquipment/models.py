from django.db import models
from config.models import Asset


class InvestigativeDetails(models.Model):
    asset_id = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="investigative_details",
        db_column="asset_ptr_id",
        primary_key=True,
    )
    item_description = models.TextField(
        db_column="Item_Description", blank=True, null=True
    )
    par_id = models.CharField(max_length=100, db_column="ParID", blank=True, null=True)
    office = models.CharField(max_length=255, db_column="Office", blank=True, null=True)

    class Meta:
        db_table = "Investigative_Details"

    def __str__(self):
        return f"Details for {self.asset_id}"


class InspectionLog(models.Model):
    inspection_id = models.AutoField(primary_key=True, db_column="InspectionID")
    inspection_date = models.DateField(db_column="Inspection_Date")
    compliance_status = models.CharField(max_length=100, db_column="Compliance_Status")
    next_inspection_date = models.DateField(
        db_column="Next_Inspection_Date", blank=True, null=True
    )
    inspector_id = models.CharField(max_length=100, db_column="InspectorID")

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="inspection_logs",
        db_column="AssetID",
    )

    class Meta:
        db_table = "Inspection_Log"

    def __str__(self):
        return f"Log {self.inspection_id} for Asset {self.asset.asset_id}"


class ICSRecord(models.Model):
    ics_id = models.AutoField(primary_key=True)
    ics_number = models.CharField(max_length=100, blank=True, null=True)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    issued_to = models.CharField(max_length=255, blank=True, null=True)
    date_issued = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="inves_ics_records",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "Investigative_ICS_Record"

    def __str__(self):
        return f"ICS {self.ics_number}"


class InvestigativeActivityLog(models.Model):
    log_id = models.AutoField(primary_key=True)

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="investigative_activity_logs",
        db_column="asset_ptr_id",
        null=True,
        blank=True,
        db_constraint=False,
    )

    action = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Investigative_Activity_Log"

    def __str__(self):
        return f"{self.action} - {self.asset_id}"


class InvestigativePARRecord(models.Model):
    par_id = models.AutoField(primary_key=True)
    par_number = models.CharField(max_length=100, blank=True, null=True)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    issued_to = models.CharField(max_length=255, blank=True, null=True)
    date_issued = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name="inves_par_records",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "Investigative_PAR_Record"

    def __str__(self):
        return f"PAR {self.par_number}"
