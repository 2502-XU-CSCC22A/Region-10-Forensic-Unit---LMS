from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Vehicle
from config.models import Asset, Category, AssetStatus

@receiver(post_save, sender=Vehicle)
def sync_vehicle_to_assets(sender, instance, created, **kwargs):
    if created:
        category, _ = Category.objects.get_or_create(category_name="VEHICLE")
        
        status = AssetStatus.objects.filter(name__icontains="Active").first()

        Asset.objects.create(
            property_no=instance.plate_number or instance.conduction_number or instance.vehicle_id,
            model=f"{instance.make} {instance.model}",
            serial_no=instance.chassis_number or instance.vehicle_id,
            date_acquired=timezone.now().date(),
            category=category,
            status=status,
        )