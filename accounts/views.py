from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import AccountForm
from .models import Account


@method_decorator(login_required, name='dispatch')
class AccountListView(ListView):
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 10  # Pagination with 10 accounts per page

    def get_queryset(self):
        # Filter accounts by logged-in user
        queryset = Account.objects.filter(user=self.request.user)

        # Order by name or balance (we'll order by name by default)
        ordering = self.request.GET.get('ordering', 'name')
        if ordering == 'balance':
            queryset = queryset.order_by('-balance')
        else:
            queryset = queryset.order_by('name')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate summary data for the cards
        all_accounts = Account.objects.filter(user=self.request.user)

        # Total balance of all accounts
        total_balance = all_accounts.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')

        # Number of active accounts
        active_accounts_count = all_accounts.filter(is_active=True).count()

        # Account with highest balance
        highest_balance_account = all_accounts.filter(
            is_active=True
        ).order_by('-balance').first()

        context.update({
            'total_balance': total_balance,
            'active_accounts_count': active_accounts_count,
            'highest_balance_account': highest_balance_account,
            'breadcrumb_items': [
                {'title': 'Contas', 'active': True}
            ]
        })

        return context

@method_decorator(login_required, name='dispatch')
class AccountCreateView(CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:list')

    def form_valid(self, form):
        # Associate the account with the current user
        form.instance.user = self.request.user
        messages.success(self.request, 'Conta criada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Criar Conta'
        context['button_text'] = 'Criar Conta'
        context['breadcrumb_items'] = [
            {'title': 'Contas', 'url': reverse_lazy('accounts:list')},
            {'title': 'Nova Conta', 'active': True}
        ]
        return context

@method_decorator(login_required, name='dispatch')
class AccountUpdateView(UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:list')

    def get_queryset(self):
        # Ensure users can only edit their own accounts
        return Account.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Conta atualizada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Conta'
        context['button_text'] = 'Atualizar Conta'
        context['breadcrumb_items'] = [
            {'title': 'Contas', 'url': reverse_lazy('accounts:list')},
            {'title': 'Editar Conta', 'active': True}
        ]
        return context

@method_decorator(login_required, name='dispatch')
class AccountDeleteView(DeleteView):
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:list')

    def get_queryset(self):
        # Ensure users can only delete their own accounts
        return Account.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        # Check if there are associated transactions
        account = self.get_object()
        from transactions.models import Transaction
        associated_transactions = Transaction.objects.filter(account=account).exists()

        if associated_transactions:
            messages.error(request, 'Não é possível excluir esta conta porque ela tem transações associadas. Considere desativar a conta em vez de excluí-la.')
            return redirect('accounts:list')

        messages.success(request, 'Conta excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Contas', 'url': reverse_lazy('accounts:list')},
            {'title': 'Excluir Conta', 'active': True}
        ]
        return context
