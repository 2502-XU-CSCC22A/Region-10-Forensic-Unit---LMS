from django.db import models
from django.conf import settings
from datetime import date


class Personnel(models.Model):
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
    status_id = models.BigAutoField(primary_key=True, db_column='StatusID')
<<<<<<< HEAD
    status_name = models.CharField(max_length=50, db_column='Status_Name', unique=True)

    class Meta:
        db_table = 'Asset_Status'
        managed = False 

class Category(models.Model):   
    category_name = models.CharField(max_length=100, unique=True)
=======

    status_name = models.CharField(
        max_length=50,
        db_column='Status_Name',
        unique=True
    )

    class Meta:
        db_table = 'Asset_Status'
        managed = False

    def __str__(self):
        return self.status_name


class PARRecord(models.Model):

    par_id = models.BigAutoField(primary_key=True, db_column='ParID')

    par_number = models.CharField(
        max_length=100,
        db_column='PAR_Number',
        unique=True
    )

    date_issued = models.DateField(
        db_column='Date_Issued',
        default=date.today
    )

    return_date = models.DateField(
        db_column='Return_Date',
        null=True,
        blank=True
    )

    condition_on_issuance = models.TextField(
        db_column='Condition_on_Issuance'
    )

    is_active = models.BooleanField(
        db_column='Is_Active',
        default=True
    )

    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
        db_column='AssetID',
        related_name='par_records'
    )

    issued_to = models.ForeignKey(
        Personnel,
        on_delete=models.PROTECT,
        db_column='Issued_to_ID',
        related_name='received_assets'
    )

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

    ics_id = models.AutoField(primary_key=True, db_column='ICS_ID')

    ics_number = models.CharField(
        max_length=100,
        db_column='ICS_Number',
        unique=True
    )

    date_issued = models.DateField(
        db_column='Date_Issued',
        default=date.today
    )

    return_date = models.DateField(
        db_column='Return_Date',
        null=True,
        blank=True
    )

    condition_on_issuance = models.TextField(
        db_column='Condition_on_Issuance'
    )

    is_active = models.BooleanField(
        db_column='Is_Active',
        default=True
    )

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

    category_name = models.CharField(
        max_length=100,
        unique=True
    )
>>>>>>> f2b63a2 (Updated mobility module and config asset integration)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

class Asset(models.Model):
<<<<<<< HEAD
    date_acquired = models.DateField()
    property_no = models.CharField(max_length=100, unique=True)
    serial_no = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100)
    
    status = models.ForeignKey(
        'AssetStatus', 
        on_delete=models.CASCADE, 
        db_column='StatusID',   
        related_name='assets'
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='assets')
=======

    date_acquired = models.DateField(
        default=date.today
    )

    property_no = models.CharField(
        max_length=100,
        unique=True
    )

    serial_no = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    model = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )

    quantity = models.CharField(
        max_length=100,
        default='1'
    )

    status = models.ForeignKey(
        'AssetStatus',
        on_delete=models.CASCADE,
        db_column='StatusID',
        to_field='status_id',
        related_name='assets',
        default=1
    )

    office = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column='Office'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='assets',
        default=10
    )
>>>>>>> f2b63a2 (Updated mobility module and config asset integration)

    def __str__(self):
        return f"{self.property_no} - {self.model}"