from django.core.cache import cache

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


def invalidate_counters_cache(user_id):
    """
    Invalidate the cache for the counters.
    """
    cache.delete(f'counters_{user_id}')


def counters_processor(request):
    """
    Add counters to the context for all requests
    """
    if request.user.is_authenticated:
        cache_key = f'counters_{request.user.id}'
        cached_counters = cache.get(cache_key)

        if cached_counters is None:
            # Count transactions for the current user
            total_transactions = Transaction.objects.filter(
                account__user=request.user
            ).count()

            # Count accounts for the current user
            total_accounts = Account.objects.filter(
                user=request.user
            ).count()

            # Count categories for the current user (excluding defaults) + default categories
            # The number of default categories is hardcoded as 5.
            # This should be dynamic if default categories can change.
            default_categories_count = Category.objects.filter(is_default=True).count()
            total_categories = Category.objects.filter(
                user=request.user,
                is_default=False
            ).count() + default_categories_count

            cached_counters = {
                'total_transactions': total_transactions,
                'total_accounts': total_accounts,
                'total_categories': total_categories,
            }
            cache.set(cache_key, cached_counters, 600)  # Cache for 10 minutes
        
        return cached_counters

    return {}
