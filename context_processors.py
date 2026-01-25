from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


def counters_processor(request):
    """
    Add counters to the context for all requests
    """
    if request.user.is_authenticated:
        # Count transactions for the current user
        total_transactions = Transaction.objects.filter(
            account__user=request.user
        ).count()

        # Count accounts for the current user
        total_accounts = Account.objects.filter(
            user=request.user
        ).count()

        # Count categories for the current user (excluding defaults) + default categories
        total_categories = Category.objects.filter(
            user=request.user,
            is_default=False
        ).count() + 5  # Add default categories

        return {
            'total_transactions': total_transactions,
            'total_accounts': total_accounts,
            'total_categories': total_categories,
        }

    return {}
