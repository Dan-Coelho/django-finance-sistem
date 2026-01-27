import pytest
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from model_bakery import baker

from users.models import CustomUser
from accounts.models import Account

@pytest.mark.django_db
def test_account_creation():
    """
    Teste de criação de conta.
    """
    user = baker.make(CustomUser)
    account = baker.make(Account, user=user, name='Conta Corrente', balance=1000.00)
    assert account.user == user
    assert account.name == 'Conta Corrente'
    assert account.balance == 1000.00
    assert account.is_active is True

@pytest.mark.django_db
def test_account_balance_min_value_validation():
    """
    Teste de validação de balance (MinValueValidator).
    """
    user = baker.make(CustomUser)
    with pytest.raises(ValidationError):
        account = baker.make(Account, user=user, name='Conta Inválida', balance=-100.00)
        account.full_clean() # Triggers model validation

@pytest.mark.django_db
def test_account_name_cannot_be_empty():
    """
    Teste de validação: name não pode ser vazio.
    """
    user = baker.make(CustomUser)
    with pytest.raises(ValidationError, match="Name cannot be empty."):
        account = baker.make(Account, user=user, name=' ')
        account.clean()

@pytest.mark.django_db
def test_account_unique_together_validation():
    """
    Teste de validação unique_together (user, name).
    """
    user = baker.make(CustomUser)
    baker.make(Account, user=user, name='Conta Repetida')
    with pytest.raises(IntegrityError):
        baker.make(Account, user=user, name='Conta Repetida')

@pytest.mark.django_db
def test_account_user_relationship():
    """
    Teste de relacionamento com User.
    """
    user = baker.make(CustomUser, email='test_user@example.com')
    account = baker.make(Account, user=user, name='Minha Conta')
    assert account.user == user
    assert account.user.email == 'test_user@example.com'

@pytest.mark.django_db
def test_account_str_method():
    """
    Teste do método __str__ da conta.
    """
    user = baker.make(CustomUser, email='str_user@example.com')
    account = baker.make(Account, user=user, name='Conta Teste')
    assert str(account) == f"Conta Teste ({user.email})"

@pytest.mark.django_db
def test_account_description_is_optional():
    """
    Teste de que a descrição da conta é opcional.
    """
    user = baker.make(CustomUser)
    account = baker.make(Account, user=user, name='Sem Descrição', description='')
    assert account.description == ''