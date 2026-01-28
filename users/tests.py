import pytest
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.db.utils import IntegrityError
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from model_bakery import baker

from users.models import CustomUser
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


# Existing fixtures (from model tests)
@pytest.fixture
def user():
    return baker.make(CustomUser)

@pytest.fixture
def account(user):
    return baker.make(Account, user=user, balance=Decimal('1000.00'))

@pytest.fixture
def income_category(user):
    return baker.make(Category, user=user, type=Category.INCOME)

@pytest.fixture
def expense_category(user):
    return baker.make(Category, user=user, type=Category.EXPENSE)

# New fixtures for view tests
@pytest.fixture
def logged_in_user(client):
    user = CustomUser.objects.create_user(email='testuser@example.com', password='password123')
    client.login(email='testuser@example.com', password='password123')
    return user

@pytest.fixture
def other_user(client):
    user = CustomUser.objects.create_user(email='otheruser@example.com', password='password123')
    return user

@pytest.fixture
def dashboard_data_user(client):
    user = CustomUser.objects.create_user(email='dashboard@example.com', password='password123')
    client.login(email='dashboard@example.com', password='password123')
    account = baker.make(Account, user=user, balance=Decimal('5000.00'), is_active=True)
    
    # Categories
    income_cat = baker.make(Category, user=user, name='Salário', type=Category.INCOME)
    expense_cat_food = baker.make(Category, user=user, name='Alimentação', type=Category.EXPENSE)
    expense_cat_transport = baker.make(Category, user=user, name='Transporte', type=Category.EXPENSE)

    # Transactions for current month
    today = timezone.now().date()
    baker.make(Transaction, account=account, category=income_cat, type=Transaction.INCOME, amount=Decimal('2000.00'), date=today)
    baker.make(Transaction, account=account, category=expense_cat_food, type=Transaction.EXPENSE, amount=Decimal('300.00'), date=today - timedelta(days=5))
    baker.make(Transaction, account=account, category=expense_cat_transport, type=Transaction.EXPENSE, amount=Decimal('150.00'), date=today - timedelta(days=10))

    # Transactions for last month
    last_month = today.replace(day=1) - timedelta(days=1)
    baker.make(Transaction, account=account, category=income_cat, type=Transaction.INCOME, amount=Decimal('1500.00'), date=last_month)
    baker.make(Transaction, account=account, category=expense_cat_food, type=Transaction.EXPENSE, amount=Decimal('200.00'), date=last_month - timedelta(days=5))

    # Inactive account
    baker.make(Account, user=user, balance=Decimal('100.00'), is_active=False)

    return user

# Model tests (already implemented above)
@pytest.mark.django_db
def test_create_user():
    """
    Teste de criação de usuário.
    """
    user = CustomUser.objects.create_user(email='test@example.com', password='password123')
    assert user.email == 'test@example.com'
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.check_password('password123')

@pytest.mark.django_db
def test_create_user_no_email_raises_error():
    """
    Teste de email obrigatório.
    """
    with pytest.raises(ValueError, match='O email é obrigatório'):
        CustomUser.objects.create_user(email=None, password='password123')

@pytest.mark.django_db
def test_create_duplicate_email_raises_error():
    """
    Teste de email único.
    """
    baker.make(CustomUser, email='duplicate@example.com')
    with pytest.raises(IntegrityError): # or ValueError depending on where validation occurs
        CustomUser.objects.create_user(email='duplicate@example.com', password='password123')

@pytest.mark.django_db
def test_create_superuser():
    """
    Teste de criação de superuser.
    """
    superuser = CustomUser.objects.create_superuser(email='admin@example.com', password='adminpassword')
    assert superuser.email == 'admin@example.com'
    assert superuser.is_active is True
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.check_password('adminpassword')

@pytest.mark.django_db
def test_create_superuser_with_is_staff_false_raises_error():
    """
    Teste de superuser com is_staff=False levanta erro.
    """
    with pytest.raises(ValueError, match='Superuser precisa ter is_staff=True'):
        CustomUser.objects.create_superuser(email='admin@example.com', password='adminpassword', is_staff=False)

@pytest.mark.django_db
def test_create_superuser_with_is_superuser_false_raises_error():
    """
    Teste de superuser com is_superuser=False levanta erro.
    """
    with pytest.raises(ValueError, match='Superuser precisa ter is_superuser=True'):
        CustomUser.objects.create_superuser(email='admin@example.com', password='adminpassword', is_superuser=False)

@pytest.mark.django_db
def test_user_str_method():
    """
    Teste do método __str__ do usuário.
    """
    user = baker.make(CustomUser, email='str_test@example.com')
    assert str(user) == 'str_test@example.com'


# --- Authentication View Tests ---

@pytest.mark.django_db
def test_signup_view_get(client):
    """
    Teste GET para a view de cadastro.
    """
    response = client.get(reverse('users:signup'))
    assert response.status_code == 200
    assert 'registration/signup.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_signup_view_post_valid_data(client):
    """
    Teste POST com dados válidos para a view de cadastro.
    """
    data = {
        'email': 'newuser@example.com',
        'password': 'password123',
        'password2': 'password123',
    }
    response = client.post(reverse('users:signup'), data, follow=True)
    assert response.status_code == 200 # Should redirect to dashboard and then render
    assert CustomUser.objects.filter(email='newuser@example.com').exists()
    assert response.context['user'].is_authenticated # User should be logged in
    # Check for redirection to dashboard (LOGIN_REDIRECT_URL)
    assert response.redirect_chain[0][0] == reverse('users:dashboard')

@pytest.mark.django_db
def test_signup_view_post_invalid_data(client):
    """
    Teste POST com dados inválidos para a view de cadastro (senhas não coincidem).
    """
    data = {
        'email': 'invalid@example.com',
        'password': 'password123',
        'password2': 'differentpassword',
    }
    response = client.post(reverse('users:signup'), data)
    assert response.status_code == 200
    assert not CustomUser.objects.filter(email='invalid@example.com').exists()
    assert 'registration/signup.html' in [t.name for t in response.templates] # Form should re-render with errors

@pytest.mark.django_db
def test_signup_view_post_duplicate_email(client):
    """
    Teste POST com email duplicado para a view de cadastro.
    """
    baker.make(CustomUser, email='existing@example.com')
    data = {
        'email': 'existing@example.com',
        'password': 'password123',
        'password2': 'password123',
    }
    response = client.post(reverse('users:signup'), data)
    assert response.status_code == 200
    assert 'registration/signup.html' in [t.name for t in response.templates]
    # Check that no new user was created
    assert CustomUser.objects.filter(email='existing@example.com').count() == 1


@pytest.mark.django_db
def test_login_view_get(client):
    """
    Teste GET para a view de login.
    """
    response = client.get(reverse('users:login'))
    assert response.status_code == 200
    assert 'registration/login.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_login_view_post_valid_credentials(client):
    """
    Teste POST com credenciais válidas para a view de login.
    """
    user = CustomUser.objects.create_user(email='testlogin@example.com', password='validpassword')
    data = {
        'email': 'testlogin@example.com',
        'password': 'validpassword',
    }
    response = client.post(reverse('users:login'), data, follow=True)
    assert response.status_code == 200
    assert response.context['user'].is_authenticated
    assert response.context['user'] == user
    assert response.redirect_chain[0][0] == reverse('users:dashboard')

@pytest.mark.django_db
def test_login_view_post_invalid_credentials(client):
    """
    Teste POST com credenciais inválidas para a view de login.
    """
    CustomUser.objects.create_user(email='badlogin@example.com', password='correctpassword')
    data = {
        'email': 'badlogin@example.com',
        'password': 'wrongpassword',
    }
    response = client.post(reverse('users:login'), data)
    assert response.status_code == 200
    assert not response.context['user'].is_authenticated
    assert 'registration/login.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_logout_view(client):
    """
    Teste para a view de logout.
    """
    user = CustomUser.objects.create_user(email='testlogout@example.com', password='password123')
    client.login(email='testlogout@example.com', password='password123') # Log in the user

    response = client.post(reverse('users:logout'), follow=True) # Use POST for logout
    assert response.status_code == 200
    assert not response.context['user'].is_authenticated
    # Should redirect to landing page (LOGOUT_REDIRECT_URL)
    assert response.redirect_chain[0][0] == reverse('users:landing_page')


# --- Password Reset View Tests ---
# Note: Full password reset flow testing requires mocking email backend or inspecting mail.
# These tests focus on basic view accessibility and form submission.

@pytest.mark.django_db
def test_password_reset_view_get(client):
    """
    Teste GET para a view de solicitação de redefinição de senha.
    """
    response = client.get(reverse('users:password_reset'))
    assert response.status_code == 200
    assert 'registration/password_reset_form.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_password_reset_view_post_valid_email(client, mailoutbox, settings):
    """
    Teste POST com email válido para a view de solicitação de redefinição de senha.
    """
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend' # Use in-memory email backend for testing
    baker.make(CustomUser, email='reset@example.com')
    data = {'email': 'reset@example.com'}
    response = client.post(reverse('users:password_reset'), data, follow=True)
    assert response.status_code == 200
    assert len(mailoutbox) == 1 # An email should be sent
    assert mailoutbox[0].to == ['reset@example.com']
    assert response.redirect_chain[0][0] == reverse('users:password_reset_done')

@pytest.mark.django_db
def test_password_reset_view_post_invalid_email(client, mailoutbox):
    """
    Teste POST com email inválido (não existente) para a view de solicitação de redefinição de senha.
    """
    data = {'email': 'nonexistent@example.com'}
    response = client.post(reverse('users:password_reset'), data, follow=True)
    assert response.status_code == 200
    assert len(mailoutbox) == 0 # No email should be sent
    assert response.redirect_chain[0][0] == reverse('users:password_reset_done') # Still redirects to done page for security

@pytest.mark.django_db
def test_password_reset_done_view_get(client):
    """
    Teste GET para a view de confirmação de envio de email de redefinição.
    """
    response = client.get(reverse('users:password_reset_done'))
    assert response.status_code == 200
    assert 'registration/password_reset_done.html' in [t.name for t in response.templates]


# --- Dashboard View Tests ---

@pytest.mark.django_db
def test_dashboard_view_authenticated_access(client, dashboard_data_user):
    """
    Teste de acesso autenticado ao dashboard.
    """
    response = client.get(reverse('users:dashboard'))
    assert response.status_code == 200
    assert 'dashboard.html' in [t.name for t in response.templates]
    assert response.context['total_balance'] is not None

@pytest.mark.django_db
def test_dashboard_view_unauthenticated_access(client):
    """
    Teste de acesso não autenticado ao dashboard (deve redirecionar para login).
    """
    response = client.get(reverse('users:dashboard'))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('users:dashboard')}"

@pytest.mark.django_db
@patch('users.views.cache') # Mock the cache to control its behavior in tests
def test_dashboard_card_calculations_current_month(mock_cache, client, dashboard_data_user):
    """
    Teste de cálculos dos cards do dashboard para o período 'current_month'.
    """
    mock_cache.get.return_value = None # Ensure cache is not used
    mock_cache.set.return_value = None

    response = client.get(reverse('users:dashboard'))
    context = response.context

    # Get data from fixture for verification
    user_account = Account.objects.get(user=dashboard_data_user, is_active=True)
    
    # Expected values for current month (based on dashboard_data_user fixture)
    expected_total_balance = user_account.balance # Initial 5000 + 2000 income - 300 food - 150 transport = 6550
    # Recalculate based on current setup. initial is 5000.00
    # +2000.00 (income) -300.00 (food) -150.00 (transport) = 6550.00
    # last month: +1500.00 (income) -200.00 (food) = 1300.00
    # so total is 6550.00 - 1300.00 = 5250
    
    # No, model bakery's baker.make creates and saves.
    # The balance on the account fixture is the *initial* balance
    # The transactions made in dashboard_data_user fixture for current month will update the account's balance
    # 5000 (initial) + 2000 (income) - 300 (food) - 150 (transport) = 6550.00 (current balance)

    user_account.refresh_from_db() # Refresh to get actual balance after all transactions
    assert context['total_balance'] == user_account.balance

    # For current month:
    # Income: 2000.00
    # Expenses: 300.00 + 150.00 = 450.00
    # Balance: 2000.00 - 450.00 = 1550.00
    assert context['monthly_income'] == Decimal('2000.00')
    assert context['monthly_expenses'] == Decimal('450.00')
    assert context['monthly_balance'] == Decimal('1550.00')

    # Avg daily expenses: 450 / (days from start of month to today)
    today = timezone.now().date()
    start_date = today.replace(day=1)
    days_in_period = (today - start_date).days + 1
    if days_in_period > 0:
        expected_avg_daily_expenses = Decimal('450.00') / days_in_period
    else:
        expected_avg_daily_expenses = Decimal('0.00')
    assert context['avg_daily_expenses'] == expected_avg_daily_expenses.quantize(Decimal('0.01')) # Quantize for comparison

    # Highest expense category (Food: 300.00, Transport: 150.00)
    assert context['highest_expense_category']['category__name'] == 'Alimentação'
    assert context['highest_expense_category']['total'] == Decimal('300.00')

    # Recent transactions (should be 3 for current month)
    assert len(context['recent_transactions']) == 3

    # Chart data
    assert 'Alimentação' in context['chart_categories']
    assert 'Transporte' in context['chart_categories']
    assert Decimal('300.00') in context['chart_amounts']
    assert Decimal('150.00') in context['chart_amounts']

@pytest.mark.django_db
@patch('users.views.cache')
def test_dashboard_card_calculations_last_month(mock_cache, client, dashboard_data_user):
    """
    Teste de cálculos dos cards do dashboard para o período 'last_month'.
    """
    mock_cache.get.return_value = None
    mock_cache.set.return_value = None

    response = client.get(reverse('users:dashboard') + '?period=last_month')
    context = response.context

    # For last month:
    # Income: 1500.00
    # Expenses: 200.00
    # Balance: 1500.00 - 200.00 = 1300.00
    assert context['monthly_income'] == Decimal('1500.00')
    assert context['monthly_expenses'] == Decimal('200.00')
    assert context['monthly_balance'] == Decimal('1300.00')

@pytest.mark.django_db
@patch('users.views.cache')
def test_dashboard_card_calculations_custom_period(mock_cache, client, dashboard_data_user):
    """
    Teste de cálculos dos cards do dashboard para um período 'customizado'.
    """
    mock_cache.get.return_value = None
    mock_cache.set.return_value = None

    # Define a custom period that includes only one income transaction (2000.00)
    today = timezone.now().date()
    start_date_str = (today - timedelta(days=2)).strftime('%Y-%m-%d')
    end_date_str = (today - timedelta(days=2)).strftime('%Y-%m-%d') # Only one day

    response = client.get(reverse('users:dashboard') + f'?period=custom&start_date={start_date_str}&end_date={end_date_str}')
    context = response.context

    # Income: 0 (assuming the 2000 income was today)
    # Expenses: 0
    # Balance: 0
    assert context['monthly_income'] == Decimal('0.00')
    assert context['monthly_expenses'] == Decimal('0.00')
    assert context['monthly_balance'] == Decimal('0.00')