import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from transactions.models import Transaction

from .forms import AccountForm
from .models import Account

logger = logging.getLogger(__name__)

class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 10

    def get_queryset(self):
        queryset = Account.objects.filter(user=self.request.user).select_related('user')
        ordering = self.request.GET.get('ordering', 'name')
        if ordering == 'balance':
            queryset = queryset.order_by('-balance')
        else:
            queryset = queryset.order_by('name')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the full queryset to perform aggregations
        all_accounts_qs = self.get_queryset()

        total_balance = all_accounts_qs.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
        active_accounts_count = all_accounts_qs.filter(is_active=True).count()
        highest_balance_account = all_accounts_qs.filter(is_active=True).order_by('-balance').first()
        
        context.update({
            'total_balance': total_balance,
            'active_accounts_count': active_accounts_count,
            'highest_balance_account': highest_balance_account,
            'breadcrumb_items': [{'title': 'Contas', 'active': True}]
        })
        return context

class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Conta criada com sucesso!')
        logger.info(f"Account '{form.instance.name}' created by user '{self.request.user}'.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Criar Conta',
            'button_text': 'Criar Conta',
            'breadcrumb_items': [
                {'title': 'Contas', 'url': reverse_lazy('accounts:list')},
                {'title': 'Nova Conta', 'active': True}
            ]
        })
        return context

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:list')

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Conta atualizada com sucesso!')
        logger.info(f"Account '{form.instance.name}' updated by user '{self.request.user}'.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Editar Conta',
            'button_text': 'Atualizar Conta',
            'breadcrumb_items': [
                {'title': 'Contas', 'url': reverse_lazy('accounts:list')},
                {'title': 'Editar Conta', 'active': True}
            ]
        })
        return context

class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:list')

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        account = self.object
        
        if Transaction.objects.filter(account=account).exists():
            messages.error(request, 'Não é possível excluir esta conta porque ela tem transações associadas. Considere desativar a conta em vez de excluí-la.')
            return redirect('accounts:list')
        
        account_name = account.name
        messages.success(request, 'Conta excluída com sucesso!')
        logger.info(f"Account '{account_name}' deleted by user '{request.user}'.")
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Contas', 'url': reverse_lazy('accounts:list')},
            {'title': 'Excluir Conta', 'active': True}
        ]
        return context

