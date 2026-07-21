from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache

from context_processors import invalidate_counters_cache

from .models import Category


@receiver(post_save, sender=Category)
def on_category_save(sender, instance, **kwargs):
    """
    Invalidate the counters cache when a category is saved.
    Also, invalidate the default_categories cache if a default category is changed.
    """
    if instance.is_default:
        cache.delete('default_categories')
    if instance.user_id:
        invalidate_counters_cache(instance.user_id)


@receiver(post_delete, sender=Category)
def on_category_delete(sender, instance, **kwargs):
    """
    Invalidate the counters cache when a category is deleted.
    Also, invalidate the default_categories cache if a default category is changed.
    """
    if instance.is_default:
        cache.delete('default_categories')
    if instance.user_id:
        invalidate_counters_cache(instance.user_id)
