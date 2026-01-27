import pytest
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from model_bakery import baker
from decimal import Decimal

from users.models import CustomUser
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

@pytest.fixture
def user():
    return baker.make(CustomUser)

@pytest.fixture
def account(user):
    return baker.make(Account, user=user, balance=1000.00)

@pytest.fixture
def income_category(user):
    return baker.make(Category, user=user, type=Category.INCOME)

@pytest.fixture
def expense_category(user):
    return baker.make(Category, user=user, type=Category.EXPENSE)

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
        amount=100.00,
        date=timezone.now().date(),
        description='Salário do mês'
    )
    assert transaction.account == account
    assert transaction.category == income_category
    assert transaction.type == Transaction.INCOME
    assert transaction.amount == 100.00
    assert transaction.description == 'Salário do mês'

@pytest.mark.django_db
def test_transaction_amount_min_value_validation(account, income_category):
    """
    Teste de validação de valor mínimo (amount > 0).
    """
    with pytest.raises(ValidationError, match='Amount must be greater than 0.'):
        transaction = baker.make(
            Transaction,
            account=account,
            category=income_category,
            type=Transaction.INCOME,
            amount=0.00
        )
        transaction.full_clean()

@pytest.mark.django_db
def test_transaction_date_future_validation(account, income_category):
    """
    Teste de validação: data não pode ser futura.
    """
    future_date = timezone.now().date() + timedelta(days=1)
    with pytest.raises(ValidationError, match='Date cannot be in the future.'):
        transaction = baker.make(
            Transaction,
            account=account,
            category=income_category,
            type=Transaction.INCOME,
            amount=50.00,
            date=future_date
        )
        transaction.full_clean()

@pytest.mark.django_db
def test_transaction_category_type_match_validation(account, income_category, expense_category):
    """
    Teste de validação: category.type deve corresponder a transaction.type.
    """
    # Trying to create an INCOME transaction with an EXPENSE category
    with pytest.raises(ValidationError, match='Category type .* must match transaction type .*'):
        transaction = baker.make(
            Transaction,
            account=account,
            category=expense_category,
            type=Transaction.INCOME,
            amount=50.00
        )
        transaction.full_clean()
    
    # Trying to create an EXPENSE transaction with an INCOME category
    with pytest.raises(ValidationError, match='Category type .* must match transaction type .*'):
        transaction = baker.make(
            Transaction,
            account=account,
            category=income_category,
            type=Transaction.EXPENSE,
            amount=50.00
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
        amount=200.00
    )
    account.refresh_from_db()
    assert account.balance == initial_balance + 200.00

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
        amount=150.00
    )
    account.refresh_from_db()
    assert account.balance == initial_balance - 150.00

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
        amount=100.00
    )
    account.refresh_from_db()
    assert account.balance == initial_balance + 100.00

    # Update amount
    transaction.amount = 150.00
    transaction.save()
    account.refresh_from_db()
    assert account.balance == initial_balance + 150.00 # original balance + new amount

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
        amount=100.00
    )
    account.refresh_from_db()
    assert account.balance == initial_balance + 100.00

    # Change type from INCOME to EXPENSE
    transaction.type = Transaction.EXPENSE
    transaction.category = expense_category # Must also change category to match new type
    transaction.save()
    account.refresh_from_db()
    # Initial balance (1000) - original income (100) + new expense (100) = 800
    # or initial_balance - 100 (revert old income) - 100 (apply new expense)
    assert account.balance == initial_balance - 100.00

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
        amount=200.00
    )
    account.refresh_from_db()
    assert account.balance == initial_balance + 200.00

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
        amount=150.00
    )
    account.refresh_from_db()
    assert account.balance == initial_balance - 150.00

    transaction.delete()
    account.refresh_from_db()
    assert account.balance == initial_balance # Balance should revert to initial

@pytest.mark.django_db
def test_transaction_account_relationship(account, income_category):
    """
    Teste de relacionamento com Account.
    """
    transaction = baker.make(Transaction, account=account, category=income_category, type=Transaction.INCOME, amount=50.00)
    assert transaction.account == account

@pytest.mark.django_db
def test_transaction_category_relationship(account, income_category):
    """
    Teste de relacionamento com Category.
    """
    transaction = baker.make(Transaction, account=account, category=income_category, type=Transaction.INCOME, amount=50.00)
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