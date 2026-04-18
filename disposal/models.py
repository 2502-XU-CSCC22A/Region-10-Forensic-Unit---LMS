from django.db import models

class DisposalItem(models.Model):
    unit = models.CharField(max_length=100)
    sub_unit = models.CharField(max_length=100)
    comm_type = models.CharField(max_length=100) # You can store "Fantasy, Fiction" here
    expiry_status = models.DateField()
    station_url = models.URLField()

    def __str__(self):
        return self.sub_unit

class BerItem(models.Model):
    # Mapping to your filter categories
    CATEGORY_CHOICES = [
        ('firearm', 'Firearm'),
        ('communication', 'Communication'),
        ('investigative', 'Investigative'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category})"