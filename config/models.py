from django.db import models

class AssetStatus(models.Model):
    """
    Independent lookup table for Asset Statuses.
    Matches 'Asset_Status' in your ERD.
    """
    status_name = models.CharField(
        max_length=50, 
        db_column='StatusName',  # Matches Supabase column name
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