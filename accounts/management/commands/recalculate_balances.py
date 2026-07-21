from django.core.management.base import BaseCommand
from django.db.models import Sum, Case, When, DecimalField
from accounts.models import Account
from transactions.models import Transaction

class Command(BaseCommand):
    help = 'Recalculates the balance for all accounts'

    def handle(self, *args, **options):
        self.stdout.write('Starting balance recalculation...')
        
        for account in Account.objects.all():
            # Calculate the total income and expenses for the account
            totals = Transaction.objects.filter(account=account).aggregate(
                total_income=Sum(
                    Case(
                        When(type=Transaction.INCOME, then='amount'),
                        default=0,
                        output_field=DecimalField()
                    )
                ),
                total_expense=Sum(
                    Case(
                        When(type=Transaction.EXPENSE, then='amount'),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            )
            
            total_income = totals.get('total_income') or 0
            total_expense = totals.get('total_expense') or 0
            
            # Calculate the new balance
            new_balance = total_income - total_expense
            
            # Update the account balance
            if account.balance != new_balance:
                account.balance = new_balance
                account.save(update_fields=['balance'])
                self.stdout.write(self.style.SUCCESS(f'Account "{account.name}" balance updated to {new_balance}'))
            else:
                self.stdout.write(self.style.NOTICE(f'Account "{account.name}" balance is already correct.'))

        self.stdout.write(self.style.SUCCESS('Balance recalculation finished.'))
