from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, date
from datetime import timedelta
from accounts.models import Account
from transactions.models import Transaction
from decimal import Decimal
from .forms import SignUpForm, LoginForm


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
        login(self.request, user)  # Log the user in automatically after signup
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
    next_page = reverse_lazy('landing_page')  # Redirect to landing page after logout

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
        end_date = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    else:
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Ensure start_date is a datetime object with time set to start of day
    if isinstance(start_date, date):
        start_date = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    else:
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

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
    ).values('category__name', 'category__color').annotate(
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

    context = {
        'total_balance': total_balance,
        'monthly_income': period_income,
        'monthly_expenses': period_expenses,
        'monthly_balance': period_balance,
        'recent_transactions': recent_transactions,
        'chart_categories': chart_categories,
        'chart_amounts': chart_amounts,
        'chart_colors': chart_colors,
        'has_expense_data': len(chart_categories) > 0,
        'selected_period': period,
        'start_date': start_date_str or start_date.strftime('%Y-%m-%d') if start_date and hasattr(start_date, 'strftime') else '',
        'end_date': end_date_str or end_date.strftime('%Y-%m-%d') if end_date and hasattr(end_date, 'strftime') else '',
    }

    return render(request, 'dashboard.html', context)


def landing_page(request):
    """
    View for the landing page that redirects authenticated users to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    return render(request, 'landing.html')
