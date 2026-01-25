from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction as db_transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import TransactionFilterForm, TransactionForm
from .models import Account, Transaction


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            account__user=self.request.user
        ).select_related('account', 'category').order_by('-date', '-created_at')

        # Apply filters if present
        account_id = self.request.GET.get('account')
        category_id = self.request.GET.get('category')
        transaction_type = self.request.GET.get('type')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        search_query = self.request.GET.get('search')

        if account_id:
            queryset = queryset.filter(account_id=account_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if transaction_type and transaction_type != 'all':
            queryset = queryset.filter(type=transaction_type)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if search_query:
            queryset = queryset.filter(
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(account__name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate totals for filtered transactions
        transactions = self.get_queryset()
        total_income = sum(t.amount for t in transactions if t.type == 'INCOME')
        total_expense = sum(t.amount for t in transactions if t.type == 'EXPENSE')
        balance = total_income - total_expense

        context.update({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'filter_form': TransactionFilterForm(user=self.request.user, data=self.request.GET or None),
            'breadcrumb_items': [
                {'title': 'Transações', 'active': True}
            ]
        })

        return context


# Placeholder for the dashboard view that was originally in this file
@login_required
def dashboard(request):
    # This is a placeholder - the actual dashboard should be in a separate app or in users app
    return render(request, 'transactions/dashboard.html')


class CreateIncomeView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.type = 'INCOME'
        response = super().form_valid(form)
        messages.success(self.request, 'Receita criada com sucesso!')

        # Check if "Salvar e Nova Receita" was clicked
        if 'continue' in self.request.POST:
            return redirect('transactions:create-income')
        return response

    def get_success_url(self):
        return reverse_lazy('transactions:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['transaction_type'] = 'INCOME'
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Transações', 'url': reverse_lazy('transactions:list')},
            {'title': 'Nova Receita', 'active': True}
        ]
        return context


class CreateExpenseView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.type = 'EXPENSE'
        response = super().form_valid(form)
        messages.success(self.request, 'Despesa criada com sucesso!')

        # Check if "Salvar e Nova Despesa" was clicked
        if 'continue' in self.request.POST:
            return redirect('transactions:create-expense')
        return response

    def get_success_url(self):
        return reverse_lazy('transactions:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['transaction_type'] = 'EXPENSE'
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Transações', 'url': reverse_lazy('transactions:list')},
            {'title': 'Nova Despesa', 'active': True}
        ]
        return context


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:list')

    def form_valid(self, form):
        # Ensure the transaction belongs to the current user
        transaction = self.get_object()
        if transaction.account.user != self.request.user:
            messages.error(self.request, 'Você não pode editar esta transação.')
            return redirect('transactions:list')

        # Store the original values for balance calculation
        original_transaction = Transaction.objects.get(pk=transaction.pk)

        # Perform the update within a transaction
        with db_transaction.atomic():
            response = super().form_valid(form)

            # Log the changes (optional - just for demonstration)
            messages.success(self.request, 'Transação atualizada com sucesso!')
            return response

    def get_queryset(self):
        # Only allow updating transactions that belong to the current user
        return Transaction.objects.filter(account__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        # Pass the transaction type from the instance
        if self.object:
            kwargs['transaction_type'] = self.object.type
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Transações', 'url': reverse_lazy('transactions:list')},
            {'title': 'Editar Transação', 'active': True}
        ]
        return context


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:list')

    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        if transaction.account.user != request.user:
            messages.error(request, 'Você não pode excluir esta transação.')
            return redirect('transactions:list')

        # Get the account balance before deletion for messaging
        account_before = transaction.account
        balance_before = account_before.balance

        # Perform the deletion (the signal will update the balance)
        response = super().delete(request, *args, **kwargs)

        # Get the account balance after deletion
        try:
            account_after = Account.objects.get(pk=account_before.pk)
            balance_after = account_after.balance
            messages.success(request, f'Transação excluída com sucesso! Saldo alterado de R${balance_before:.2f} para R${balance_after:.2f}.')
        except Account.DoesNotExist:
            messages.success(request, 'Transação excluída com sucesso!')

        return response

    def get_queryset(self):
        # Only allow deleting transactions that belong to the current user
        return Transaction.objects.filter(account__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = self.get_object()

        # Calculate the balance after deletion (opposite effect of the transaction)
        if transaction.type == 'INCOME':
            new_balance = transaction.account.balance - transaction.amount
        else:  # EXPENSE
            new_balance = transaction.account.balance + transaction.amount

        context['balance_after_deletion'] = new_balance
        context['breadcrumb_items'] = [
            {'title': 'Transações', 'url': reverse_lazy('transactions:list')},
            {'title': 'Excluir Transação', 'active': True}
        ]
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        # Only allow viewing transactions that belong to the current user
        return Transaction.objects.filter(account__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction = self.get_object()

        # Add related information to the context
        context['related_transactions'] = Transaction.objects.filter(
            account=transaction.account
        ).exclude(pk=transaction.pk).order_by('-date')[:5]  # Last 5 transactions in the same account

        context['breadcrumb_items'] = [
            {'title': 'Transações', 'url': reverse_lazy('transactions:list')},
            {'title': 'Detalhes da Transação', 'active': True}
        ]
        return context
