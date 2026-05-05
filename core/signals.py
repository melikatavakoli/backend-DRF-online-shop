from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.models import BaseUser


@receiver(pre_save, sender=BaseUser)
def cache_previous_name_fields(sender, instance, **kwargs):
    if not instance.pk:
        return
    previous = (
        sender.objects.filter(pk=instance.pk)
        .values("first_name", "last_name", "mobile")
        .first()
    )
    instance._prev_name_fields = previous
