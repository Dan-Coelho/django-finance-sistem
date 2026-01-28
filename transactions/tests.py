from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from model_bakery import baker

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction
from users.models import CustomUser

from .forms import TransactionForm


@pytest.fixture
def logged_in_user(client):
    user = CustomUser.objects.create_user(email='testuser@example.com', password='password123')
    client.logout() # Ensure a clean slate
    client.login(email='testuser@example.com', password='password123')
    return user

@pytest.fixture
def other_user(client):
    user = CustomUser.objects.create_user(email='otheruser@example.com', password='password123')
    return user

@pytest.fixture
def user_account(logged_in_user):
    return baker.make(Account, user=logged_in_user, balance=Decimal('1000.00'))

@pytest.fixture
def other_user_account(other_user):
    return baker.make(Account, user=other_user, balance=Decimal('500.00'))

@pytest.fixture
def user_income_category(logged_in_user):
    return baker.make(Category, user=logged_in_user, type=Category.INCOME)

@pytest.fixture
def user_expense_category(logged_in_user):
    return baker.make(Category, user=logged_in_user, type=Category.EXPENSE)

# Original model fixtures
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


# Model tests (already implemented above)
@pytest.mark.django_db
def test_transaction_creation(account, income_category):
    """
    Teste de criação de transação.
    """
    transaction = baker.make(
        Transaction,
        account=account,
        category=income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00'), # Use Decimal
        date=timezone.now().date(),
        description='Salário do mês'
    )
    assert transaction.account == account
    assert transaction.category == income_category
    assert transaction.type == Transaction.INCOME
    assert transaction.amount == Decimal('100.00')
    assert transaction.description == 'Salário do mês'

@pytest.mark.django_db
def test_transaction_amount_min_value_validation(account, income_category):
    """
    Teste de validação de valor mínimo (amount > 0).
    """
    with pytest.raises(ValidationError):
        transaction = baker.make(
            Transaction,
            account=account,
            category=income_category,
            type=Transaction.INCOME,
            amount=Decimal('0.00') # Use Decimal
        )
        transaction.full_clean()

@pytest.mark.django_db
def test_transaction_date_future_validation(account, income_category):
    """
    Teste de validação: data não pode ser futura.
    """
    future_date = timezone.now().date() + timedelta(days=1)
    with pytest.raises(ValidationError):
        transaction = baker.make(
            Transaction,
            account=account,
            category=income_category,
            type=Transaction.INCOME,
            amount=Decimal('50.00'), # Use Decimal
            date=future_date
        )
        transaction.full_clean()

@pytest.mark.django_db
def test_transaction_category_type_match_validation(account, income_category, expense_category):
    """
    Teste de validação: category.type deve corresponder a transaction.type.
    """
    # Trying to create an INCOME transaction with an EXPENSE category
    with pytest.raises(ValidationError):
        transaction = baker.make(
            Transaction,
            account=account,
            category=expense_category,
            type=Transaction.INCOME,
            amount=Decimal('50.00') # Use Decimal
        )
        transaction.full_clean()
    
    # Trying to create an EXPENSE transaction with an INCOME category
    with pytest.raises(ValidationError):
        transaction = baker.make(
            Transaction,
            account=account,
            category=income_category,
            type=Transaction.EXPENSE,
            amount=Decimal('50.00') # Use Decimal
        )
        transaction.full_clean()

@pytest.mark.django_db
def test_transaction_creation_updates_balance_income(account, income_category):
    """
    Teste de signal: criar transação de RECEITA atualiza saldo da conta.
    """
    initial_balance = account.balance
    baker.make(
        Transaction,
        account=account,
        category=income_category,
        type=Transaction.INCOME,
        amount=Decimal('200.00') # Use Decimal
    )
    account.refresh_from_db()
    assert account.balance == initial_balance + Decimal('200.00')

@pytest.mark.django_db
def test_transaction_creation_updates_balance_expense(account, expense_category):
    """
    Teste de signal: criar transação de DESPESA atualiza saldo da conta.
    """
    initial_balance = account.balance
    baker.make(
        Transaction,
        account=account,
        category=expense_category,
        type=Transaction.EXPENSE,
        amount=Decimal('150.00') # Use Decimal
    )
    account.refresh_from_db()
    assert account.balance == initial_balance - Decimal('150.00')

@pytest.mark.django_db
def test_transaction_update_amount_updates_balance(account, income_category):
    """
    Teste de signal: atualizar valor de transação atualiza saldo.
    """
    initial_balance = account.balance
    transaction = baker.make(
        Transaction,
        account=account,
        category=income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00') # Use Decimal
    )
    account.refresh_from_db()
    assert account.balance == initial_balance + Decimal('100.00')

    # Update amount
    transaction.amount = Decimal('150.00') # Use Decimal
    transaction.save()
    account.refresh_from_db()
    assert account.balance == initial_balance + Decimal('150.00') # original balance + new amount

@pytest.mark.django_db
def test_transaction_update_type_updates_balance(account, income_category, expense_category):
    """
    Teste de signal: mudar tipo de transação atualiza saldo.
    """
    initial_balance = account.balance
    transaction = baker.make(
        Transaction,
        account=account,
        category=income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00') # Use Decimal
    )
    account.refresh_from_db()
    assert account.balance == initial_balance + Decimal('100.00')

    # Change type from INCOME to EXPENSE
    transaction.type = Transaction.EXPENSE
    transaction.category = expense_category # Must also change category to match new type
    transaction.save()
    account.refresh_from_db()
    assert account.balance == initial_balance - Decimal('100.00') # Test expects initial - 100, so new balance should be initial - 100

@pytest.mark.django_db
def test_transaction_delete_updates_balance_income(account, income_category):
    """
    Teste de signal: deletar transação de RECEITA atualiza saldo.
    """
    initial_balance = account.balance
    transaction = baker.make(
        Transaction,
        account=account,
        category=income_category,
        type=Transaction.INCOME,
        amount=Decimal('200.00') # Use Decimal
    )
    account.refresh_from_db()
    assert account.balance == initial_balance + Decimal('200.00')

    transaction.delete()
    account.refresh_from_db()
    assert account.balance == initial_balance # Balance should revert to initial

@pytest.mark.django_db
def test_transaction_delete_updates_balance_expense(account, expense_category):
    """
    Teste de signal: deletar transação de DESPESA atualiza saldo.
    """
    initial_balance = account.balance
    transaction = baker.make(
        Transaction,
        account=account,
        category=expense_category,
        type=Transaction.EXPENSE,
        amount=Decimal('150.00') # Use Decimal
    )
    account.refresh_from_db()
    assert account.balance == initial_balance - Decimal('150.00')

    transaction.delete()
    account.refresh_from_db()
    assert account.balance == initial_balance # Balance should revert to initial

@pytest.mark.django_db
def test_transaction_account_relationship(account, income_category):
    """
    Teste de relacionamento com Account.
    """
    transaction = baker.make(Transaction, account=account, category=income_category, type=Transaction.INCOME, amount=Decimal('50.00')) # Use Decimal
    assert transaction.account == account

@pytest.mark.django_db
def test_transaction_category_relationship(account, income_category):
    """
    Teste de relacionamento com Category.
    """
    transaction = baker.make(Transaction, account=account, category=income_category, type=Transaction.INCOME, amount=Decimal('50.00')) # Use Decimal
    assert transaction.category == income_category

@pytest.mark.django_db
def test_transaction_str_method(account, income_category):
    """
    Teste do método __str__ da transação.
    """
    transaction = baker.make(
        Transaction,
        account=account,
        category=income_category,
        type=Transaction.INCOME,
        amount=Decimal('123.45'),
        date=timezone.localdate()
    )
    assert str(transaction) == f"Receita - 123.45 - {timezone.localdate()}"


# --- Transaction View Tests (CRUD) ---

@pytest.mark.django_db
def test_transaction_list_view_authenticated_access(client, logged_in_user, user_account, user_income_category):
    """
    Teste de acesso autenticado à listagem de transações.
    """
    baker.make(Transaction, account=user_account, category=user_income_category, type=Category.INCOME, _quantity=3)
    response = client.get(reverse('transactions:list'))
    assert response.status_code == 200
    assert 'transactions/transaction_list.html' in [t.name for t in response.templates]
    assert len(response.context['transactions']) == 3

@pytest.mark.django_db
def test_transaction_list_view_unauthenticated_access(client):
    """
    Teste de acesso não autenticado à listagem de transações (deve redirecionar para login).
    """
    response = client.get(reverse('transactions:list'))
    assert response.status_code == 302 # Redirect
    assert response.url == f"{reverse('users:login')}?next={reverse('transactions:list')}"

@pytest.mark.django_db
def test_transaction_list_view_displays_only_own_transactions(client, logged_in_user, user_account, other_user_account, user_income_category):
    """
    Teste se a listagem de transações exibe apenas as transações do usuário logado.
    """
    baker.make(Transaction, account=user_account, category=user_income_category, type=Category.INCOME, _quantity=2)
    baker.make(Transaction, account=other_user_account, category=user_income_category, type=Category.INCOME, _quantity=1) # Transaction for another user

    response = client.get(reverse('transactions:list'))
    assert response.status_code == 200
    assert len(response.context['transactions']) == 2
    for transaction in response.context['transactions']:
        assert transaction.account.user == logged_in_user

@pytest.mark.django_db
def test_transaction_list_view_empty_state(client, logged_in_user):
    """
    Teste de estado vazio na listagem de transações.
    """
    response = client.get(reverse('transactions:list'))
    assert response.status_code == 200
    assert len(response.context['transactions']) == 0


@pytest.mark.django_db
def test_create_income_view_authenticated_get(client, logged_in_user):
    """
    Teste GET autenticado para a view de criação de receita.
    """
    response = client.get(reverse('transactions:create_income'))
    assert response.status_code == 200
    assert 'transactions/transaction_form.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_create_income_view_unauthenticated_get(client):
    """
    Teste GET não autenticado para a view de criação de receita.
    """
    response = client.get(reverse('transactions:create_income'))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('transactions:create_income')}"

@pytest.mark.django_db
def test_create_income_view_authenticated_post_valid_data(client, logged_in_user, user_account, user_income_category):
    """
    Teste POST autenticado com dados válidos para a view de criação de receita.
    """
    initial_balance = user_account.balance
    data = {
        'account': user_account.pk,
        'category': user_income_category.pk,
        'amount': 250.00,
        'date': timezone.now().date(),
        'description': 'Receita de teste',
        'type': 'INCOME'
    }
    response = client.post(reverse('transactions:create_income'), data, follow=True)
    assert response.status_code == 200
    assert Transaction.objects.filter(account=user_account, description='Receita de teste', type=Transaction.INCOME).exists()
    user_account.refresh_from_db()
    assert user_account.balance == initial_balance + Decimal('250.00')

@pytest.mark.django_db
def test_create_income_view_authenticated_post_invalid_data(client, logged_in_user, user_account, user_income_category):
    """
    Teste POST autenticado com dados inválidos (amount=0) para a view de criação de receita.
    """
    data = {
        'account': user_account.pk,
        'category': user_income_category.pk,
        'amount': 0.00, # Invalid amount
        'date': timezone.now().date(),
        'description': 'Receita inválida',
        'type': 'INCOME'
    }
    response = client.post(reverse('transactions:create_income'), data)
    assert response.status_code == 200
    assert not Transaction.objects.filter(description='Receita inválida').exists()
    assert 'transactions/transaction_form.html' in [t.name for t in response.templates]
    assert 'amount' in response.context['form'].errors


@pytest.mark.django_db
def test_create_expense_view_authenticated_get(client, logged_in_user):
    """
    Teste GET autenticado para a view de criação de despesa.
    """
    response = client.get(reverse('transactions:create_expense'))
    assert response.status_code == 200
    assert 'transactions/transaction_form.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_create_expense_view_unauthenticated_get(client):
    """
    Teste GET não autenticado para a view de criação de despesa.
    """
    response = client.get(reverse('transactions:create_expense'))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('transactions:create_expense')}"

@pytest.mark.django_db
def test_create_expense_view_authenticated_post_valid_data(client, logged_in_user, user_account, user_expense_category):
    """
    Teste POST autenticado com dados válidos para a view de criação de despesa.
    """
    initial_balance = user_account.balance
    data = {
        'account': user_account.pk,
        'category': user_expense_category.pk,
        'amount': 100.00,
        'date': timezone.now().date(),
        'description': 'Despesa de teste',
        'type': 'EXPENSE'
    }
    response = client.post(reverse('transactions:create_expense'), data, follow=True)
    assert response.status_code == 200
    assert Transaction.objects.filter(account=user_account, description='Despesa de teste', type=Transaction.EXPENSE).exists()
    user_account.refresh_from_db()
    assert user_account.balance == initial_balance - Decimal('100.00')

@pytest.mark.django_db
def test_create_expense_view_authenticated_post_invalid_data(client, logged_in_user, user_account, user_expense_category):
    """
    Teste POST autenticado com dados inválidos (data futura) para a view de criação de despesa.
    """
    future_date = timezone.now().date() + timedelta(days=1)
    data = {
        'account': user_account.pk,
        'category': user_expense_category.pk,
        'amount': 50.00,
        'date': future_date, # Invalid date
        'description': 'Despesa inválida',
        'type': 'EXPENSE'
    }
    response = client.post(reverse('transactions:create_expense'), data)
    assert response.status_code == 200
    assert not Transaction.objects.filter(description='Despesa inválida').exists()
    assert 'transactions/transaction_form.html' in [t.name for t in response.templates]
    assert 'date' in response.context['form'].errors


@pytest.mark.django_db
def test_transaction_update_view_authenticated_get_own_transaction(client, logged_in_user, user_account, user_income_category):
    """
    Teste GET autenticado para editar transação própria.
    """
    transaction = baker.make(
        Transaction,
        account=user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    response = client.get(reverse('transactions:edit', kwargs={'pk': transaction.pk}))
    assert response.status_code == 200 
    assert 'transactions/transaction_form.html' in [t.name for t in response.templates]
    assert response.context['form'].instance == transaction

@pytest.mark.django_db
def test_transaction_update_view_unauthenticated_get(client, user_account, user_income_category):
    """
    Teste GET não autenticado para editar transação.
    """
    transaction = baker.make(
        Transaction,
        account=user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    client.logout()
    response = client.get(reverse('transactions:edit', kwargs={'pk': transaction.pk}))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('transactions:edit', kwargs={'pk': transaction.pk})}"

@pytest.mark.django_db
def test_transaction_update_view_authenticated_get_other_users_transaction(client, logged_in_user, other_user_account, user_income_category):
    """
    Teste GET autenticado para editar transação de outro usuário (deve retornar 404).
    """
    transaction_other = baker.make(
        Transaction,
        account=other_user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    response = client.get(reverse('transactions:edit', kwargs={'pk': transaction_other.pk}))
    assert response.status_code == 404

@pytest.mark.django_db
def test_transaction_update_view_authenticated_post_valid_data(client, logged_in_user, user_account, user_income_category):
    """
    Teste POST autenticado com dados válidos para editar transação própria.
    """
    initial_balance = user_account.balance
    transaction = baker.make(
        Transaction,
        account=user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    user_account.refresh_from_db() 
    assert user_account.balance == initial_balance + Decimal('100.00')

    data = {
        'account': user_account.pk,
        'category': user_income_category.pk,
        'amount': 250.00, # Updated amount
        'date': transaction.date,
        'description': 'Receita atualizada',
        'type': 'INCOME'
    }
    response = client.post(reverse('transactions:edit', kwargs={'pk': transaction.pk}), data, follow=True)
    assert response.status_code == 200
    transaction.refresh_from_db()
    assert transaction.amount == Decimal('250.00')
    assert transaction.description == 'Receita atualizada'
    user_account.refresh_from_db()
    assert user_account.balance == initial_balance + Decimal('250.00') 

@pytest.mark.django_db
def test_transaction_update_view_authenticated_post_invalid_data(client, logged_in_user, user_account, user_income_category):
    """
    Teste POST autenticado com dados inválidos para editar transação própria.
    """
    transaction = baker.make(
        Transaction,
        account=user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    data = {
        'account': user_account.pk,
        'category': user_income_category.pk,
        'amount': 0.00, # Invalid amount
        'date': transaction.date,
        'description': 'Receita inválida',
        'type': 'INCOME'
    }
    response = client.post(reverse('transactions:edit', kwargs={'pk': transaction.pk}), data)
    assert response.status_code == 200
    transaction.refresh_from_db()
    assert transaction.amount == Decimal('100.00') # Should not be updated
    assert 'transactions/transaction_form.html' in [t.name for t in response.templates]
    assert 'amount' in response.context['form'].errors


@pytest.mark.django_db
def test_transaction_delete_view_authenticated_get_own_transaction(client, logged_in_user, user_account, user_income_category):
    """
    Teste GET autenticado para deletar transação própria.
    """
    transaction = baker.make(
        Transaction,
        account=user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    response = client.get(reverse('transactions:delete', kwargs={'pk': transaction.pk}))
    assert response.status_code == 200 
    assert 'transactions/transaction_confirm_delete.html' in [t.name for t in response.templates]
    assert response.context['object'] == transaction

@pytest.mark.django_db
def test_transaction_delete_view_unauthenticated_get(client, user_account, user_income_category):
    """
    Teste GET não autenticado para deletar transação.
    """
    transaction = baker.make(
        Transaction,
        account=user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    client.logout()
    response = client.get(reverse('transactions:delete', kwargs={'pk': transaction.pk}))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('transactions:delete', kwargs={'pk': transaction.pk})}"

@pytest.mark.django_db
def test_transaction_delete_view_authenticated_get_other_users_transaction(client, logged_in_user, other_user_account, user_income_category):
    """
    Teste GET autenticado para deletar transação de outro usuário (deve retornar 404).
    """
    transaction_other = baker.make(
        Transaction,
        account=other_user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    response = client.get(reverse('transactions:delete', kwargs={'pk': transaction_other.pk}))
    assert response.status_code == 404

@pytest.mark.django_db
def test_transaction_delete_view_authenticated_post_own_transaction(client, logged_in_user, user_account, user_income_category):
    """
    Teste POST autenticado para deletar transação própria.
    """
    initial_balance = user_account.balance
    transaction = baker.make(
        Transaction,
        account=user_account,
        category=user_income_category,
        type=Transaction.INCOME,
        amount=Decimal('100.00')
    )
    user_account.refresh_from_db()
    assert user_account.balance == initial_balance + Decimal('100.00')

    response = client.post(reverse('transactions:delete', kwargs={'pk': transaction.pk}), follow=True)
    assert response.status_code == 200
    assert not Transaction.objects.filter(pk=transaction.pk).exists()
    user_account.refresh_from_db()
    assert user_account.balance == initial_balance # Balance should revert
    assert response.redirect_chain[0][0] == reverse('transactions:list')

# --- Form Tests ---
@pytest.mark.django_db
class TestTransactionForm:
    def test_transaction_form_valid_data(self, logged_in_user, user_account, user_income_category):
        """
        Test that the TransactionForm is valid with correct data.
        """
        form = TransactionForm(data={
            'amount': 100.00,
            'date': date.today(),
            'category': user_income_category.pk,
            'account': user_account.pk,
            'description': 'Valid transaction',
            'type': 'INCOME'
        }, user=logged_in_user, transaction_type='INCOME')
        assert form.is_valid()

    def test_transaction_form_amount_zero(self, logged_in_user, user_account, user_income_category):
        """
        Test that the TransactionForm raises a validation error for an amount of zero.
        """
        form = TransactionForm(data={
            'amount': 0.00,
            'date': date.today(),
            'category': user_income_category.pk,
            'account': user_account.pk,
            'description': 'Invalid amount',
            'type': 'INCOME'
        }, user=logged_in_user, transaction_type='INCOME')
        assert not form.is_valid()
        assert 'amount' in form.errors
        assert form.errors['amount'][0] == 'O valor deve ser maior que zero.'

    def test_transaction_form_future_date(self, logged_in_user, user_account, user_income_category):
        """
        Test that the TransactionForm raises a validation error for a future date.
        """
        form = TransactionForm(data={
            'amount': 100.00,
            'date': date.today() + timedelta(days=1),
            'category': user_income_category.pk,
            'account': user_account.pk,
            'description': 'Future transaction',
            'type': 'INCOME'
        }, user=logged_in_user, transaction_type='INCOME')
        assert not form.is_valid()
        assert 'date' in form.errors
        assert form.errors['date'][0] == 'A data não pode ser futura.'

    def test_transaction_form_mismatched_category_type(self, logged_in_user, user_account, user_expense_category):
        """
        Test that the TransactionForm raises a validation error for mismatched category and transaction types.
        """
        form = TransactionForm(data={
            'amount': 100.00,
            'date': date.today(),
            'category': user_expense_category.pk,
            'account': user_account.pk,
            'description': 'Mismatched type',
            'type': 'INCOME'
        }, user=logged_in_user, transaction_type='INCOME')
        assert not form.is_valid()
        assert '__all__' in form.errors
        assert form.errors['__all__'][0] == 'A categoria deve ser do mesmo tipo da transação.'