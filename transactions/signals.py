from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Transaction


@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    """
    Update the account balance when a transaction is saved.
    For income transactions, add the amount to the balance.
    For expense transactions, subtract the amount from the balance.
    """
    account = instance.account

    if instance.type == Transaction.INCOME:
        # For income, add the amount to the balance
        account.balance = F('balance') + instance.amount
    else:
        # For expense, subtract the amount from the balance
        account.balance = F('balance') - instance.amount

    account.save(update_fields=['balance'])


@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    """
    Update the account balance when a transaction is deleted.
    For income transactions, subtract the amount from the balance.
    For expense transactions, add the amount back to the balance.
    """
    account = instance.account

    if instance.type == Transaction.INCOME:
        # For income, subtract the amount from the balance (reverse the effect)
        account.balance = F('balance') - instance.amount
    else:
        # For expense, add the amount back to the balance (reverse the effect)
        account.balance = F('balance') + instance.amount

    account.save(update_fields=['balance'])
