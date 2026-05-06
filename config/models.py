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
    status_name = models.CharField(max_length=50, db_column='Status_Name', unique=True)

    class Meta:
        db_table = 'Asset_Status'
        managed = False 

class Category(models.Model):   
    category_name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

class Asset(models.Model):
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

    def __str__(self):
        return f"{self.property_no} - {self.model}"