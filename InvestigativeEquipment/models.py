from django.db import models
from config.models import Asset


class InvestigativeDetails(models.Model):
    asset_id = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='investigative_details',
        db_column='asset_ptr_id',
        primary_key=True
    )
    item_description = models.TextField(db_column='Item_Description', blank=True, null=True)
    par_id = models.CharField(max_length=100, db_column='ParID', blank=True, null=True)

    class Meta:
        db_table = 'Investigative_Details'

    def __str__(self):
        return f"Details for {self.asset_id}"


class InspectionLog(models.Model):
    inspection_id = models.AutoField(primary_key=True, db_column='InspectionID')
    inspection_date = models.DateField(db_column='Inspection_Date')
    compliance_status = models.CharField(max_length=100, db_column='Compliance_Status')
    next_inspection_date = models.DateField(db_column='Next_Inspection_Date', blank=True, null=True)
    inspector_id = models.CharField(max_length=100, db_column='InspectorID')

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='inspection_logs',
        db_column='AssetID'
    )

    class Meta:
        db_table = 'Inspection_Log'

    def __str__(self):
        return f"Log {self.inspection_id} for Asset {self.asset.asset_id}"