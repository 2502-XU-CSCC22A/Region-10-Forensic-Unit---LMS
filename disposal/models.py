from django.db import models
from django.conf import settings
from config.models import Asset

class DisposalItem(Asset): 
    """
    Inherits from Asset. 
    In the database, this creates a table with a pointer (AssetID) to the parent Asset table.
    """
    # Fields matching your 'Disposal_Log' ERD and Supabase updates
    disposal_reason = models.TextField(
        db_column='disposal_reason', 
        help_text="Reason for disposal/BER",
        null=True, 
        blank=True,
    )
    disposal_date = models.DateTimeField(
        db_column='disposal_date', 
        auto_now_add=True
    )
    days_overdue = models.IntegerField(
        db_column='days_overdue', 
        default=0, 
        null=True, 
        blank=True
    )
    expiry_date = models.DateField(
        db_column='expiry_date', 
        null=True, 
        blank=True
    )

    # Tracking the User (From your ERD Disposal_Log -> UserID)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='processed_by',
        null=True, 
        blank=True,
        related_name='disposed_items'
    )

    class Meta:
        db_table = 'disposal_disposalitems' # Matches your Supabase table name
        verbose_name = "Disposal Item"

    def __str__(self):
        return f"Disposal: {self.property_no} - {self.reason[:20]}"