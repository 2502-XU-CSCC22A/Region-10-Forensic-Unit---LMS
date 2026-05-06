from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vehicle
from config.models import AssetStatus

@receiver(post_save, sender=Vehicle)
def sync_disposal_status(sender, instance, **kwargs):
    if instance.status == "Disposed":
        try:
            disposed_status = AssetStatus.objects.get(status_name='Disposed')
            if instance.asset.status != disposed_status:
                instance.asset.status = disposed_status
                instance.asset.save()
        except AssetStatus.DoesNotExist:
            pass

        try:
            from disposal.models import DisposalItem
            DisposalItem.objects.get_or_create(
                property_no=instance.asset.property_no,
                defaults={
                    "disposal_reason": "Auto-synced from Mobility",
                    "expiry_date": getattr(instance, "registration_renewal_date", None),
                },
            )
        except (ModuleNotFoundError, ImportError):
            pass