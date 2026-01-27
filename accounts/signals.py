from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from context_processors import invalidate_counters_cache

from .models import Account


@receiver(post_save, sender=Account)
def on_account_save(sender, instance, **kwargs):
    """
    Invalidate the counters cache when an account is saved.
    """
    if instance.user_id:
        invalidate_counters_cache(instance.user_id)


@receiver(post_delete, sender=Account)
def on_account_delete(sender, instance, **kwargs):
    """
    Invalidate the counters cache when an account is deleted.
    """
    if instance.user_id:
        invalidate_counters_cache(instance.user_id)
