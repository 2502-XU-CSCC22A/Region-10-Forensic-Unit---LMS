from django.db import models

class AssetStatus(models.Model):
    status_id = models.AutoField(
        primary_key=True,
        db_column='StatusID'
    )
    status_name = models.CharField(
        max_length=50,
        db_column='Status_Name',  # note: Supabase shows "Status_Name" not "StatusName"
        unique=True
    )

    class Meta:
        db_table = 'Asset_Status'  # Matches Supabase table name
        verbose_name_plural = "Asset Statuses"

    def __str__(self):
        return self.status_name


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = "Categories"


class Asset(models.Model):
    date_acquired = models.DateField(null=True, blank=True)
    property_no   = models.CharField(max_length=100, unique=True)
    serial_no     = models.CharField(max_length=100, unique=True)
    model         = models.CharField(max_length=100)
    quantity      = models.IntegerField(default=1)
    office        = models.CharField(max_length=100, null=True, blank=True, db_column='Office')
    status        = models.ForeignKey(
                        AssetStatus,
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        db_column='StatusID',
                        related_name='assets'
                    )
    category      = models.ForeignKey(
                        Category,
                        on_delete=models.SET_NULL,  
                        null=True,
                        blank=True,
                        related_name='assets'
                    )

    class Meta:
        db_table = 'config_asset'

    def __str__(self):
        return f"{self.property_no} - {self.model}"