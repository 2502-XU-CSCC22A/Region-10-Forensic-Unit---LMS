from django.db import models
from django.conf import settings
from datetime import date

class Personnel(models.Model):
    # Matches PersonnelID PK from your diagram
    personnel_id = models.BigAutoField(primary_key=True, db_column='PersonnelID')
    name = models.CharField(max_length=255, db_column='Name')
    rank = models.CharField(max_length=100, db_column='Rank')
    badge_number = models.CharField(max_length=50, db_column='Badge_Number', unique=True)
    department = models.CharField(max_length=100, db_column='Department')

    class Meta:
        db_table = 'Personnel'

    def __str__(self):
        return f"{self.rank} {self.name}"

class AssetStatus(models.Model):
    # Use BigAutoField for the primary key to match Supabase's int8
    status_id = models.BigAutoField(primary_key=True, db_column='StatusID') 
    status_name = models.CharField(max_length=50, db_column='StatusName', unique=True)

    class Meta:
        db_table = 'Asset_Status'

    def __str__(self):
        return self.status_name

class PARRecord(models.Model):

    par_id = models.AutoField(primary_key=True, db_column='ParID')
    par_number = models.CharField(max_length=100, db_column='PAR_Number', unique=True)
    date_issued = models.DateField(db_column='Date_Issued', default=date.today)
    return_date = models.DateField(db_column='Return_Date', null=True, blank=True)
    condition_on_issuance = models.TextField(db_column='Condition_on_Issuance')
    is_active = models.BooleanField(db_column='Is_Active', default=True)

    # Foreign Keys linking to other tables
    # asset_id: Links to the specific equipment being issued
    asset = models.ForeignKey(
        'Asset', 
        on_delete=models.CASCADE, 
        db_column='AssetID', 
        related_name='par_records'
    )
    
    # issued_to_id: The personnel/staff receiving the asset
    # Note: If you have a Personnel model, link it here. Otherwise, it links to User.
    issued_to = models.ForeignKey(
        Personnel,
        on_delete=models.PROTECT,
        db_column='Issued_to_ID',
        related_name='received_assets'
    )

    # user_id: Remains linked to the Logistics Officer (Django User)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='UserID',
        related_name='authorized_pars'
    )

    class Meta:
        db_table = 'PAR_Record'
        verbose_name = "PAR Record"
        verbose_name_plural = "PAR Records"

    def __str__(self):
        return f"PAR #{self.par_number} - {self.asset.model}"

class ICSRecord(models.Model):

    ics_id = models.AutoField(primary_key=True, db_column='IcsID')
    ics_number = models.CharField(max_length=100, db_column='ICS_Number', unique=True)
    date_issued = models.DateField(db_column='Date_Issued', default=date.today)
    return_date = models.DateField(db_column='Return_Date', null=True, blank=True)
    condition_on_issuance = models.TextField(db_column='Condition_on_Issuance')
    is_active = models.BooleanField(db_column='Is_Active', default=True)

    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
        db_column='AssetID',
        related_name='ics_records'
    )

    issued_to = models.ForeignKey(
        Personnel,
        on_delete=models.PROTECT,
        db_column='Issued_to_ID',
        related_name='received_ics_assets'
    )

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='UserID',
        related_name='authorized_ics'
    )

    class Meta:
        db_table = 'ICS_Record'
        verbose_name = "ICS Record"
        verbose_name_plural = "ICS Records"

    def __str__(self):
        return f"ICS #{self.ics_number} - {self.asset.model}"

        
class Category(models.Model):   
    category_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"


class Asset(models.Model):
    # Core attributes from your diagram
    date_acquired = models.DateField()
    property_no = models.CharField(max_length=100, unique=True)
    serial_no = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100)
    
    # NEW: Link to independent AssetStatus table
    # We use db_column='StatusID' to match the Foreign Key column in Supabase
    status = models.ForeignKey(
        AssetStatus, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='StatusID', 
        related_name='assets'
    )

    # The connection to the Category table
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='assets')

    def __str__(self):
        return f"{self.property_no} - {self.model}"