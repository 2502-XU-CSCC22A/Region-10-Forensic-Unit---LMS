from django.db import models
from django.conf import settings
from config.models import Asset
from datetime import date
from config.models import Personnel
from django.contrib.auth.models import User

class UserProfile(models.Model):
    role = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.role}"
    
class DisposalItem(Asset): 
    last_sync = models.DateTimeField(auto_now=True)
    disposal_reason = models.TextField(
        db_column='disposal_reason', 
        help_text="Reason for disposal/BER",
        null=False, 
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
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='processed_by',
        null=True, 
        blank=True,
        related_name='disposed_items'
    )
    personnel_assigned = models.ForeignKey(
        Personnel,
        on_delete=models.SET_NULL,
        null=True,
        db_column='personnel_assigned'
    )

    class Meta:
        db_table = 'disposal_disposalitems' 
        verbose_name = "Disposal Item"
    
    @property
    def days_overdue_calc(self):
        if self.expiry_date and self.expiry_date < date.today():
            delta = date.today() - self.expiry_date
            return delta.days
        return 0

    def __str__(self):
        return f"Disposal: {self.property_no} - {self.reason[:20]}"
    
class DisposalActivityLog(models.Model):
    ACTION_CHOICES = [
        ('REMOVE', 'Finalized Removal'),
        ('UPDATE', 'Updated Disposal Info'),
        ('FLAGGED', 'Flagged for Disposal'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='disposal_logs'
    )

    asset = models.ForeignKey(
        Asset, 
        on_delete=models.SET_NULL, 
        null=True
    )
    
    description = models.TextField()
    disposal_reason = models.TextField(null=True, blank=True)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES, default='REMOVE')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action_type} - {self.timestamp.strftime('%Y-%m-%d')}"
