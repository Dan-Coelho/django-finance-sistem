import csv
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction as db_transaction
from django.db.models import Q
from django.http import HttpResponse
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

logger = logging.getLogger(__name__)


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
        response = super().form_valid(form)
        messages.success(self.request, 'Receita criada com sucesso!')
        logger.info(f"Income transaction '{form.instance.description}' created by user '{self.request.user}'.")

        # Check if "Salvar e Nova Receita" was clicked
        if 'continue' in self.request.POST:
            return redirect('transactions:create-income')
        return response

    def form_invalid(self, form):
        logger.error(f"Error creating income transaction for user '{self.request.user}': {form.errors}")
        return super().form_invalid(form)

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
        response = super().form_valid(form)
        messages.success(self.request, 'Despesa criada com sucesso!')
        logger.info(f"Expense transaction '{form.instance.description}' created by user '{self.request.user}'.")

        # Check if "Salvar e Nova Despesa" was clicked
        if 'continue' in self.request.POST:
            return redirect('transactions:create-expense')
        return response
    
    def form_invalid(self, form):
        logger.error(f"Error creating expense transaction for user '{self.request.user}': {form.errors}")
        return super().form_invalid(form)

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

        # Perform the update within a transaction
        with db_transaction.atomic():
            response = super().form_valid(form)

            # Log the changes (optional - just for demonstration)
            messages.success(self.request, 'Transação atualizada com sucesso!')
            logger.info(f"Transaction '{form.instance.description}' updated by user '{self.request.user}'.")
            return response

    def form_invalid(self, form):
        logger.error(f"Error updating transaction for user '{self.request.user}': {form.errors}")
        return super().form_invalid(form)
        
    def get_queryset(self):
        # Only allow updating transactions that belong to the current user
        return Transaction.objects.filter(account__user=self.request.user).select_related('account', 'category')


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
        
        transaction_description = transaction.description
        response = super().delete(request, *args, **kwargs)

        # Get the account balance after deletion
        try:
            account_after = Account.objects.get(pk=account_before.pk)
            balance_after = account_after.balance
            messages.success(request, f'Transação excluída com sucesso! Saldo alterado de R${balance_before:.2f} para R${balance_after:.2f}.')
            logger.info(f"Transaction '{transaction_description}' deleted by user '{request.user}'.")
        except Account.DoesNotExist:
            messages.success(request, 'Transação excluída com sucesso!')
            logger.info(f"Transaction '{transaction_description}' deleted by user '{request.user}'.")

        return response

    def get_queryset(self):
        # Only allow deleting transactions that belong to the current user
        return Transaction.objects.filter(account__user=self.request.user).select_related('account', 'category')

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
        return Transaction.objects.filter(account__user=self.request.user).select_related('account', 'category')

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


@login_required
def export_transactions_csv(request):
    """
    Export transactions to CSV with applied filters
    """
    # Get the same queryset as the list view with filters applied
    queryset = Transaction.objects.filter(
        account__user=request.user
    ).select_related('account', 'category').order_by('-date', '-created_at')

    # Apply filters if present (same as in TransactionListView)
    account_id = request.GET.get('account')
    category_id = request.GET.get('category')
    transaction_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search_query = request.GET.get('search')

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

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="transacoes.csv"'

    # Create CSV writer
    writer = csv.writer(response)

    # Write header row with Portuguese labels
    writer.writerow([
        'ID',
        'Tipo',
        'Valor (R$)',
        'Data',
        'Descrição',
        'Categoria',
        'Conta',
        'Criado em',
        'Atualizado em'
    ])

    # Write data rows
    for transaction in queryset:
        writer.writerow([
            transaction.id,
            transaction.get_type_display(),
            f'{transaction.amount:.2f}',
            transaction.date.strftime('%d/%m/%Y'),
            transaction.description,
            transaction.category.name,
            transaction.account.name,
            transaction.created_at.strftime('%d/%m/%Y %H:%M:%S'),
            transaction.updated_at.strftime('%d/%m/%Y %H:%M:%S')
        ])

    return response


@login_required
def export_report_pdf(request):
    """
    Export report to PDF
    """
    try:
        from datetime import date, datetime, timedelta

        from django.http import HttpResponse

        from django.template.loader import get_template
        from django.urls import reverse_lazy
        from django.utils import timezone

        from django.utils.dateparse import parse_date
        from weasyprint import CSS, HTML
        from weasyprint.text.fonts import FontConfiguration

        # Get filters from request parameters (similar to reports view)
        report_type = request.GET.get('report_type', 'summary')  # Default to summary report
        period = request.GET.get('period', 'current_month')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        category_ids = request.GET.getlist('categories')
        account_ids = request.GET.getlist('accounts')
        selected_category_id = request.GET.get('category_id')  # For category report

        # Calculate date range based on selected period
        today = timezone.now()
        start_date = None
        end_date = today

        if period == 'current_week':
            # Start from Monday of current week
            start_date = today - timedelta(days=today.weekday())
        elif period == 'current_month':
            # Start from first day of current month
            start_date = today.replace(day=1)
        elif period == 'last_month':
            # Start from first day of last month, end on last day of last month
            first_day_current_month = today.replace(day=1)
            last_day_last_month = first_day_current_month - timedelta(days=1)
            start_date = last_day_last_month.replace(day=1)
            end_date = last_day_last_month
        elif period == 'current_year':
            # Start from first day of current year
            start_date = today.replace(month=1, day=1)
        elif period == 'custom' and start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                # If dates are invalid, fall back to current month
                start_date = today.replace(day=1)
                period = 'current_month'
        else:
            # Default to current month
            start_date = today.replace(day=1)
            period = 'current_month'

        # Ensure end_date is a datetime object with time set to end of day
        if isinstance(end_date, date):
            end_date = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        else:
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Ensure start_date is a datetime object with time set to start of day
        if isinstance(start_date, date):
            start_date = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        else:
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # Build the base query for transactions
        transactions = Transaction.objects.filter(
            account__user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('account', 'category')

        # Apply category filters if specified
        if category_ids:
            transactions = transactions.filter(category_id__in=category_ids)

        # Apply account filters if specified
        if account_ids:
            transactions = transactions.filter(account_id__in=account_ids)

        # Calculate totals for filtered transactions
        total_income = sum(t.amount for t in transactions if t.type == 'INCOME')
        total_expense = sum(t.amount for t in transactions if t.type == 'EXPENSE')
        balance = total_income - total_expense

        # Get all categories and accounts for the filter dropdowns
        from categories.models import Category
        all_categories = Category.objects.filter(user=request.user)
        all_accounts = Account.objects.filter(user=request.user)

        # Prepare data based on report type
        if report_type == 'category' and selected_category_id:
            # Category report: show all transactions for a specific category
            
            selected_category = Category.objects.filter(user=request.user, id=selected_category_id).first()
            category_transactions = transactions.filter(category_id=selected_category_id).order_by('-date')

            # Calculate category totals
            category_total_income = sum(t.amount for t in category_transactions if t.type == 'INCOME')
            category_total_expense = sum(t.amount for t in category_transactions if t.type == 'EXPENSE')
            category_balance = category_total_income - category_total_expense

            # Prepare context for category report
            context = {
                'report_type': report_type,
                'selected_category': selected_category,
                'category_transactions': category_transactions,
                'category_total_income': category_total_income,
                'category_total_expense': category_total_expense,
                'category_balance': category_balance,
                'all_categories': all_categories,
                'all_accounts': all_accounts,
                'selected_period': period,
                'start_date': start_date_str or start_date.strftime('%Y-%m-%d') if start_date and hasattr(start_date, 'strftime') else '',
                'end_date': end_date_str or end_date.strftime('%Y-%m-%d') if end_date and hasattr(end_date, 'strftime') else '',
                'selected_categories': [int(id) for id in category_ids],
                'selected_accounts': [int(id) for id in account_ids],
                'selected_category_id': int(selected_category_id) if selected_category_id else None,
                'request': request,
            }

            # Load the category report template
            template = get_template('reports/category_report.html')

        elif report_type == 'cashflow':
            # Cash flow report: show daily income/expenses over time
            # Group transactions by date
            daily_data = {}
            for transaction in transactions:
                date_str = transaction.date.strftime('%Y-%m-%d')
                if date_str not in daily_data:
                    daily_data[date_str] = {'date': transaction.date, 'income': 0, 'expenses': 0, 'transactions': []}

                if transaction.type == 'INCOME':
                    daily_data[date_str]['income'] += transaction.amount
                else:
                    daily_data[date_str]['expenses'] += transaction.amount

                daily_data[date_str]['transactions'].append(transaction)

            # Sort by date
            sorted_daily_data = sorted(daily_data.values(), key=lambda x: x['date'])

            # Calculate cumulative balance
            cumulative_balance = 0
            for day_data in sorted_daily_data:
                daily_net = day_data['income'] - day_data['expenses']
                cumulative_balance += daily_net
                day_data['net'] = daily_net  # Add net value for the day
                day_data['cumulative_balance'] = cumulative_balance

            # Prepare context for cash flow report
            context = {
                'report_type': report_type,
                'daily_data': sorted_daily_data,
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': balance,
                'all_categories': all_categories,
                'all_accounts': all_accounts,
                'selected_period': period,
                'start_date': start_date_str or start_date.strftime('%Y-%m-%d') if start_date and hasattr(start_date, 'strftime') else '',
                'end_date': end_date_str or end_date.strftime('%Y-%m-%d') if end_date and hasattr(end_date, 'strftime') else '',
                'selected_categories': [int(id) for id in category_ids],
                'selected_accounts': [int(id) for id in account_ids],
                'request': request,
            }

            # Load the cash flow report template
            template = get_template('reports/cashflow_report.html')

        else:
            # Default to monthly summary report
            # Prepare data for the monthly summary report
            monthly_summary = {
                'total_income': total_income,
                'total_expense': total_expense,
                'balance': balance,
                'transactions': transactions.order_by('-date')
            }

            # Prepare context for summary report
            context = {
                'report_type': 'summary',
                'monthly_summary': monthly_summary,
                'all_categories': all_categories,
                'all_accounts': all_accounts,
                'selected_period': period,
                'start_date': start_date_str or start_date.strftime('%Y-%m-%d') if start_date and hasattr(start_date, 'strftime') else '',
                'end_date': end_date_str or end_date.strftime('%Y-%m-%d') if end_date and hasattr(end_date, 'strftime') else '',
                'selected_categories': [int(id) for id in category_ids],
                'selected_accounts': [int(id) for id in account_ids],
                'request': request,
            }

            # Load the summary report template
            template = get_template('reports/reports.html')

        # Render the template with context
        html_content = template.render(context)

        # Generate PDF
        font_config = FontConfiguration()
        html = HTML(string=html_content, base_url=request.build_absolute_uri())

        # Define CSS for print/PDF
        css = CSS(string='''
            @page {
                margin: 2cm;
                @bottom-right {
                    content: "Página " counter(page) " de " counter(pages);
                    font-size: 10px;
                    color: #666;
                }
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.4;
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 1rem;
            }
            th, td {
                padding: 0.5rem;
                text-align: left;
                border: 1px solid #ddd;
            }
            th {
                background-color: #f5f5f5;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .summary-card {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            .summary-title {
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            .summary-value {
                font-size: 1.2rem;
                font-weight: bold;
            }
            .income {
                color: green;
            }
            .expense {
                color: red;
            }
            .balance-positive {
                color: green;
            }
            .balance-negative {
                color: red;
            }
        ''', font_config=font_config)

        pdf = html.write_pdf(stylesheets=[css], font_config=font_config)

        # Create the HttpResponse object with PDF header
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_transacoes.pdf"'
        logger.info(f"PDF report generated by user '{request.user}'.")
        return response
    except Exception as e:
        logger.error(f"Error generating PDF report for user '{request.user}': {e}")
        messages.error(request, 'Ocorreu um erro ao gerar o relatório em PDF. Tente novamente mais tarde.')
        return redirect('users:reports')