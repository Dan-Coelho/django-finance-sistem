from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from context_processors import invalidate_counters_cache

from .models import Transaction
from .notify import Notify


@receiver(pre_save, sender=Transaction)
def store_pre_save_instance(sender, instance, **kwargs):
    """
    Store the original state of the transaction instance before it is saved.
    """
    if instance.pk:
        instance._pre_save_instance = Transaction.objects.get(pk=instance.pk)
    else:
        instance._pre_save_instance = None


@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    """
    Update the account balance when a transaction is saved (created or updated).
    """
    account = instance.account

    if created:
        # New transaction
        if instance.type == Transaction.INCOME:
            account.balance = F('balance') + instance.amount
        else:
            account.balance = F('balance') - instance.amount
        account.save(update_fields=['balance'])
    else:
        # Updated transaction
        pre_save_instance = instance._pre_save_instance
        if pre_save_instance:
            # Revert the old amount
            if pre_save_instance.type == Transaction.INCOME:
                account.balance = F('balance') - pre_save_instance.amount
            else:
                account.balance = F('balance') + pre_save_instance.amount
            account.save(update_fields=['balance'])

            # Apply the new amount
            account.refresh_from_db()
            if instance.type == Transaction.INCOME:
                account.balance = F('balance') + instance.amount
            else:
                account.balance = F('balance') - instance.amount
            account.save(update_fields=['balance'])

    # Invalidate the counters cache for the user
    if instance.account.user_id:
        invalidate_counters_cache(instance.account.user_id)


@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    """
    Update the account balance when a transaction is deleted.
    """
    account = instance.account

    if instance.type == Transaction.INCOME:
        account.balance = F('balance') - instance.amount
    else:
        account.balance = F('balance') + instance.amount
    account.save(update_fields=['balance'])

    # Invalidate the counters cache for the user
    if instance.account.user_id:
        invalidate_counters_cache(instance.account.user_id)

# Integração com Notify para envio de dados para webhook
@receiver(post_save, sender=Transaction)
def send_notification(sender, instance, **kwargs):
    notify = Notify()
    data = {
        'account': str(instance.account),
        'type': instance.type,
        'category': str(instance.category),
        'amount': str(instance.amount),
        'date': str(instance.date),
        'description': instance.description
    }
    notify.send_notification(data)

