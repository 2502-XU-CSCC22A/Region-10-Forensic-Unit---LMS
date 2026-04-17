from django.db import models

class Communication(models.Model):
    # 'Unit' column - likely a date or timestamp in your screenshot
    unit_date = models.DateField(null=True, blank=True)
    
    # 'Sub-Unit' column (e.g., Fire&Blood, Bridge of clay)
    sub_unit = models.CharField(max_length=255)
    
    # 'Communication Type' column (e.g., Fantasy, Fiction)
    # In a more advanced setup, you might use a ManyToMany field for tags
    comm_type = models.CharField(max_length=100, help_text="e.g., Fantasy, Fiction, Self-help")
    
    # 'Status Expiry' column
    status_expiry = models.DateField(null=True, blank=True)
    
    # 'Station' column (e.g., https://abc.in)
    station_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.sub_unit} - {self.unit_date}"