import pytest
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib import messages
from model_bakery import baker
from decimal import Decimal

from users.models import CustomUser
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction # Needed for testing deletion with related objects

# Fixtures for common test objects
@pytest.fixture
def logged_in_user(client):
    user = CustomUser.objects.create_user(email='testuser@example.com', password='password123')
    client.login(email='testuser@example.com', password='password123')
    return user

@pytest.fixture
def other_user(client):
    user = CustomUser.objects.create_user(email='otheruser@example.com', password='password123')
    return user

# Model tests (already implemented above)
@pytest.mark.django_db
def test_account_creation():
    """
    Teste de criação de conta.
    """
    user = baker.make(CustomUser)
    account = baker.make(Account, user=user, name='Conta Corrente', balance=Decimal('1000.00'))
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
        account = baker.make(Account, user=user, name='Conta Inválida', balance=Decimal('-100.00'))
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


# --- Account View Tests (CRUD) ---

@pytest.mark.django_db
def test_account_list_view_authenticated_access(client, logged_in_user):
    """
    Teste de acesso autenticado à listagem de contas.
    """
    baker.make(Account, user=logged_in_user, _quantity=3)
    response = client.get(reverse('accounts:list'))
    assert response.status_code == 200
    assert 'accounts/account_list.html' in [t.name for t in response.templates]
    assert len(response.context['accounts']) == 3

@pytest.mark.django_db
def test_account_list_view_unauthenticated_access(client):
    """
    Teste de acesso não autenticado à listagem de contas (deve redirecionar para login).
    """
    response = client.get(reverse('accounts:list'))
    assert response.status_code == 302 # Redirect
    assert response.url == f"{reverse('users:login')}?next={reverse('accounts:list')}"

@pytest.mark.django_db
def test_account_list_view_displays_only_own_accounts(client, logged_in_user, other_user):
    """
    Teste se a listagem de contas exibe apenas as contas do usuário logado.
    """
    baker.make(Account, user=logged_in_user, _quantity=2)
    baker.make(Account, user=other_user, _quantity=1) # Account for another user

    response = client.get(reverse('accounts:list'))
    assert response.status_code == 200
    assert len(response.context['accounts']) == 2
    for account in response.context['accounts']:
        assert account.user == logged_in_user

@pytest.mark.django_db
def test_account_list_view_empty_state(client, logged_in_user):
    """
    Teste de estado vazio na listagem de contas.
    """
    response = client.get(reverse('accounts:list'))
    assert response.status_code == 200
    assert len(response.context['accounts']) == 0
    # Assuming the template uses an empty_state component or message
    # assert 'Nenhuma conta encontrada.' in response.content.decode()


@pytest.mark.django_db
def test_account_create_view_authenticated_get(client, logged_in_user):
    """
    Teste GET autenticado para a view de criação de conta.
    """
    response = client.get(reverse('accounts:create'))
    assert response.status_code == 200
    assert 'accounts/account_form.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_account_create_view_unauthenticated_get(client):
    """
    Teste GET não autenticado para a view de criação de conta.
    """
    response = client.get(reverse('accounts:create'))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('accounts:create')}"

@pytest.mark.django_db
def test_account_create_view_authenticated_post_valid_data(client, logged_in_user):
    """
    Teste POST autenticado com dados válidos para a view de criação de conta.
    """
    data = {
        'name': 'Nova Conta Teste',
        'description': 'Descrição da nova conta',
        'balance': 500.00,
        'is_active': True,
    }
    response = client.post(reverse('accounts:create'), data, follow=True)
    assert response.status_code == 200 # Redirects to list view
    assert Account.objects.filter(user=logged_in_user, name='Nova Conta Teste').exists()
    assert Account.objects.get(name='Nova Conta Teste').balance == 500.00
    # Check for success message (if any, would be in messages framework)
    # assert any(m.level == messages.SUCCESS for m in response.context['messages'])

@pytest.mark.django_db
def test_account_create_view_authenticated_post_invalid_data(client, logged_in_user):
    """
    Teste POST autenticado com dados inválidos (saldo negativo) para a view de criação de conta.
    """
    data = {
        'name': 'Conta Com Erro',
        'description': 'Descrição',
        'balance': -100.00, # Invalid balance
        'is_active': True,
    }
    response = client.post(reverse('accounts:create'), data)
    assert response.status_code == 200
    assert not Account.objects.filter(user=logged_in_user, name='Conta Com Erro').exists()
    assert 'accounts/account_form.html' in [t.name for t in response.templates]
    # Check for form errors
    assert 'balance' in response.context['form'].errors


@pytest.mark.django_db
def test_account_update_view_authenticated_get_own_account(client, logged_in_user):
    """
    Teste GET autenticado para editar conta própria.
    """
    account = baker.make(Account, user=logged_in_user, name='Conta a Editar')
    response = client.get(reverse('accounts:update', kwargs={'pk': account.pk}))
    assert response.status_code == 200
    assert 'accounts/account_form.html' in [t.name for t in response.templates]
    assert response.context['form'].instance == account

@pytest.mark.django_db
def test_account_update_view_unauthenticated_get(client):
    """
    Teste GET não autenticado para editar conta.
    """
    account = baker.make(Account)
    response = client.get(reverse('accounts:update', kwargs={'pk': account.pk}))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('accounts:update', kwargs={'pk': account.pk})}"

@pytest.mark.django_db
def test_account_update_view_authenticated_get_other_users_account(client, logged_in_user, other_user):
    """
    Teste GET autenticado para editar conta de outro usuário (deve retornar 404).
    """
    account_other = baker.make(Account, user=other_user, name='Conta do Outro')
    response = client.get(reverse('accounts:update', kwargs={'pk': account_other.pk}))
    assert response.status_code == 404 # Should be 404 if object not found or permission denied

@pytest.mark.django_db
def test_account_update_view_authenticated_post_valid_data(client, logged_in_user):
    """
    Teste POST autenticado com dados válidos para editar conta própria.
    """
    account = baker.make(Account, user=logged_in_user, name='Conta Antiga', description='Desc Antiga')
    data = {
        'name': 'Conta Atualizada',
        'description': 'Desc Atualizada',
        'balance': account.balance, # balance should be readonly in form, but we pass current value
        'is_active': False,
    }
    response = client.post(reverse('accounts:update', kwargs={'pk': account.pk}), data, follow=True)
    assert response.status_code == 200
    account.refresh_from_db()
    assert account.name == 'Conta Atualizada'
    assert account.description == 'Desc Atualizada'
    assert account.is_active is False
    # Check for success message
    # assert any(m.level == messages.SUCCESS for m in response.context['messages'])

@pytest.mark.django_db
def test_account_update_view_authenticated_post_invalid_data(client, logged_in_user):
    """
    Teste POST autenticado com dados inválidos para editar conta própria.
    """
    account = baker.make(Account, user=logged_in_user, name='Conta Invalida Update')
    data = {
        'name': ' ', # Invalid name
        'description': 'Desc',
        'balance': account.balance,
        'is_active': True,
    }
    response = client.post(reverse('accounts:update', kwargs={'pk': account.pk}), data)
    assert response.status_code == 200
    account.refresh_from_db()
    assert account.name == 'Conta Invalida Update' # Should not be updated
    assert 'name' in response.context['form'].errors


@pytest.mark.django_db
def test_account_delete_view_authenticated_get_own_account(client, logged_in_user):
    """
    Teste GET autenticado para deletar conta própria.
    """
    account = baker.make(Account, user=logged_in_user, name='Conta a Deletar')
    response = client.get(reverse('accounts:delete', kwargs={'pk': account.pk}))
    assert response.status_code == 200
    assert 'accounts/account_confirm_delete.html' in [t.name for t in response.templates]
    assert response.context['object'] == account

@pytest.mark.django_db
def test_account_delete_view_unauthenticated_get(client):
    """
    Teste GET não autenticado para deletar conta.
    """
    account = baker.make(Account)
    response = client.get(reverse('accounts:delete', kwargs={'pk': account.pk}))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('accounts:delete', kwargs={'pk': account.pk})}"

@pytest.mark.django_db
def test_account_delete_view_authenticated_get_other_users_account(client, logged_in_user, other_user):
    """
    Teste GET autenticado para deletar conta de outro usuário (deve retornar 404).
    """
    account_other = baker.make(Account, user=other_user, name='Conta do Outro a Deletar')
    response = client.get(reverse('accounts:delete', kwargs={'pk': account_other.pk}))
    assert response.status_code == 404

@pytest.mark.django_db
def test_account_delete_view_authenticated_post_own_account(client, logged_in_user):
    """
    Teste POST autenticado para deletar conta própria.
    """
    account = baker.make(Account, user=logged_in_user, name='Conta para Excluir')
    response = client.post(reverse('accounts:delete', kwargs={'pk': account.pk}), follow=True)
    assert response.status_code == 200
    assert not Account.objects.filter(pk=account.pk).exists()
    assert Account.objects.count() == 0 # Only this account existed for the user
    # Check for success message
    # assert any(m.level == messages.SUCCESS for m in response.context['messages'])
    assert response.redirect_chain[0][0] == reverse('accounts:list')


@pytest.mark.django_db
def test_account_delete_view_with_transactions(client, logged_in_user):
    """
    Teste de exclusão de conta com transações associadas (deve prevenir a exclusão).
    """
    account = baker.make(Account, user=logged_in_user, name='Conta com Transações')
    income_category = baker.make(Category, user=logged_in_user, type=Category.INCOME)
    baker.make(Transaction, account=account, category=income_category, type=Transaction.INCOME, amount=100.00)

    response = client.post(reverse('accounts:delete', kwargs={'pk': account.pk}), follow=True)
    assert response.status_code == 200
    assert Account.objects.filter(pk=account.pk).exists() # Account should NOT be deleted
    assert response.redirect_chain[0][0] == reverse('accounts:list')
    assert any(m.level == messages.ERROR for m in response.context['messages'])
