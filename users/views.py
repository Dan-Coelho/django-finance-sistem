from datetime import date, datetime, timedelta
from datetime import timezone as dt_timezone
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.cache import cache
from django.db.models import Case, DecimalField, F, Q, Sum, When
from django.db.models.functions import TruncMonth
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

from .forms import EmailChangeForm, LoginForm, PasswordChangeForm, SignUpForm

User = get_user_model()


class SignUpView(CreateView):
    """
    View for user registration that handles the signup form and creates a new user.
    """
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('users:dashboard')  # Redirect to dashboard after successful signup

    def form_valid(self, form):
        """
        Override form_valid to log the user in automatically after successful registration.
        """
        user = form.save()
        login(self.request, user, backend='users.backends.EmailAuthBackend')  # Log the user in automatically after signup
        messages.success(self.request, 'Conta criada com sucesso! Bem-vindo ao nosso sistema.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        """
        Override form_invalid to show error messages when form is invalid.
        """
        messages.error(self.request, 'Por favor, corrija os erros abaixo.')
        return super().form_invalid(form)


class LoginView(LoginView):
    """
    View for user login that handles authentication.
    """
    form_class = LoginForm
    template_name = 'registration/login.html'
    next_page = reverse_lazy('users:dashboard')  # Redirect to dashboard after successful login

    def form_valid(self, form):
        """
        Override form_valid to handle the 'remember-me' functionality.
        """
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # Set session expiry to 0 (session expires when browser closes)
            self.request.session.set_expiry(0)

        messages.success(self.request, f'Bem-vindo de volta, {form.get_user().email}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Override form_invalid to show error messages when login fails.
        """
        messages.error(self.request, 'Email ou senha inválidos. Por favor, tente novamente.')
        return super().form_invalid(form)


class LogoutView(LogoutView):
    """
    View for user logout that handles the logout process.
    """
    next_page = reverse_lazy('users:landing_page')  # Redirect to landing page after logout

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to show a confirmation message after logout.
        """
        if request.user.is_authenticated:
            messages.info(request, 'Você saiu da sua conta com sucesso. Até logo!')
        return super().dispatch(request, *args, **kwargs)


@login_required
def dashboard(request):
    """
    View for the dashboard that shows financial summary for authenticated users.
    """
    # Get period from request parameters
    period = request.GET.get('period', 'current_month')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

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
        end_date = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=dt_timezone.utc)
    else:
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Ensure start_date is a datetime object with time set to start of day
    if isinstance(start_date, date):
        start_date = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=dt_timezone.utc)
    else:
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Create cache key based on user and period
    cache_key = f'dashboard_stats_{request.user.id}_{period}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}'
    cached_data = cache.get(cache_key)

    if cached_data is None:
        # Calculate total balance from all active accounts
        total_balance = Account.objects.filter(
            user=request.user,
            is_active=True
        ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')

        # Calculate income for selected period
        period_income = Transaction.objects.filter(
            account__user=request.user,
            type='INCOME',
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Calculate expenses for selected period
        period_expenses = Transaction.objects.filter(
            account__user=request.user,
            type='EXPENSE',
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Calculate period balance
        period_balance = period_income - period_expenses

        # Calculate additional metrics for task 9.1.1
        # Average daily expenses for the current period
        days_in_period = (end_date.date() - start_date.date()).days + 1
        avg_daily_expenses = period_expenses / days_in_period if days_in_period > 0 else Decimal('0.00')

        # Category with highest expense in the current period
        highest_expense_category = Transaction.objects.filter(
            account__user=request.user,
            type='EXPENSE',
            date__gte=start_date,
            date__lte=end_date
        ).select_related('category').values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total').first()

# ...

        # Monthly evolution data (last 6 months)
        six_months_ago = (today.replace(day=1) - timedelta(days=5*30)).replace(day=1)

        monthly_evolution_data = Transaction.objects.filter(
            account__user=request.user,
            date__gte=six_months_ago
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            income=Sum(Case(When(type='INCOME', then=F('amount')), default=Decimal('0.0'), output_field=DecimalField())),
            expense=Sum(Case(When(type='EXPENSE', then=F('amount')), default=Decimal('0.0'), output_field=DecimalField()))
        ).order_by('month')

        monthly_evolution = []
        for data in monthly_evolution_data:
            monthly_evolution.append({
                'month': data['month'].strftime('%b/%y'),
                'income': float(data['income']),
                'expense': float(data['expense']),
                'balance': float(data['income'] - data['expense'])
            })


        # Get recent transactions for selected period
        recent_transactions = Transaction.objects.filter(
            account__user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).select_related('account', 'category').order_by('-date')[:5]

        # Process data for expense chart for selected period
        expense_data = Transaction.objects.filter(
            account__user=request.user,
            type='EXPENSE',
            date__gte=start_date,
            date__lte=end_date
        ).select_related('category').values('category__name', 'category__color').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]

        # Prepare data for chart
        chart_categories = []
        chart_amounts = []
        chart_colors = []

        for item in expense_data:
            chart_categories.append(item['category__name'])
            chart_amounts.append(float(item['total']))
            # Convert the color from RGB to RGBA format if needed
            color = item['category__color']
            if color.startswith('rgb'):
                # Already in rgb format, just add opacity
                rgba_color = color.replace('rgb', 'rgba').replace(')', ', 0.8)')
            else:
                # Assume it's hex format, convert to rgba
                hex_color = color.lstrip('#')
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                rgba_color = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.8)'

            chart_colors.append(rgba_color)

        # Calculate counters for sidebar
        total_transactions = Transaction.objects.filter(account__user=request.user).count()
        total_accounts = Account.objects.filter(user=request.user).count()
        # Count user's custom categories (excluding defaults)
        total_categories = request.user.categories.filter(is_default=False).count() + 5  # Add default categories

        cached_data = {
            'total_balance': total_balance,
            'monthly_income': period_income,
            'monthly_expenses': period_expenses,
            'monthly_balance': period_balance,
            'avg_daily_expenses': avg_daily_expenses,
            'highest_expense_category': highest_expense_category,
            'monthly_evolution': monthly_evolution,
            'recent_transactions': recent_transactions,
            'chart_categories': chart_categories,
            'chart_amounts': chart_amounts,
            'chart_colors': chart_colors,
            'has_expense_data': len(chart_categories) > 0,
            'total_transactions': total_transactions,
            'total_accounts': total_accounts,
            'total_categories': total_categories,
        }

        # Cache for 5 minutes (300 seconds) for dashboard stats
        cache.set(cache_key, cached_data, 300)

    context = cached_data
    context.update({
        'selected_period': period,
        'start_date': start_date_str or start_date.strftime('%Y-%m-%d') if start_date and hasattr(start_date, 'strftime') else '',
        'end_date': end_date_str or end_date.strftime('%Y-%m-%d') if end_date and hasattr(end_date, 'strftime') else '',
        'breadcrumb_items': [
            {'title': 'Dashboard', 'active': True}
        ]
    })

    return render(request, 'dashboard.html', context)


def landing_page(request):
    """
    View for the landing page that redirects authenticated users to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return render(request, 'landing.html')


@login_required
def change_email(request):
    """
    View for changing user's email address.
    """
    if request.method == 'POST':
        form = EmailChangeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu e-mail foi alterado com sucesso!')
            return redirect('profiles:detail')
    else:
        form = EmailChangeForm(user=request.user)

    context = {
        'form': form,
        'breadcrumb_items': [
            {'title': 'Perfil', 'url': reverse_lazy('profiles:detail')},
            {'title': 'Alterar Email', 'active': True}
        ]
    }
    return render(request, 'users/change_email.html', context)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    View for changing user's password.
    """
    form_class = PasswordChangeForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('profiles:detail')

    def form_valid(self, form):
        messages.success(self.request, 'Sua senha foi alterada com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Perfil', 'url': reverse_lazy('profiles:detail')},
            {'title': 'Alterar Senha', 'active': True}
        ]
        return context


@login_required
def reports(request):
    """
    View for the reports page that shows financial reports for authenticated users.
    """
    # Get filters from request parameters
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
        end_date = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=dt_timezone.utc)
    else:
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Ensure start_date is a datetime object with time set to start of day
    if isinstance(start_date, date):
        start_date = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=dt_timezone.utc)
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
    all_categories = Category.objects.filter(Q(user=request.user) | Q(is_default=True))
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
            'breadcrumb_items': [
                {'title': 'Relatórios', 'url': reverse_lazy('users:reports')},
                {'title': 'Relatório por Categoria', 'active': True}
            ]
        }
        return render(request, 'reports/category_report.html', context)

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
            'breadcrumb_items': [
                {'title': 'Relatórios', 'url': reverse_lazy('users:reports')},
                {'title': 'Fluxo de Caixa', 'active': True}
            ]
        }
        return render(request, 'reports/cashflow_report.html', context)

    else:
        # Default to monthly summary report
        # Prepare data for the monthly summary report
        monthly_summary = {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'transactions': transactions.order_by('-date')
        }

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
            'breadcrumb_items': [
                {'title': 'Relatórios', 'active': True}
            ]
        }

        return render(request, 'reports/reports.html', context)