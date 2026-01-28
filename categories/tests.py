import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib import messages
from model_bakery import baker

from users.models import CustomUser
from categories.models import Category
from transactions.models import Transaction 
from accounts.models import Account 

from .forms import CategoryForm

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



@pytest.fixture
def custom_category(logged_in_user):
    return baker.make(Category, user=logged_in_user, name='Meu Aluguel', type=Category.EXPENSE)

# Model tests (already implemented above)
@pytest.mark.django_db
def test_default_category_creation():
    """
    Teste de criação de categoria padrão.
    """
    category = baker.make(Category, name='Salário', type=Category.INCOME, is_default=True, user=None)
    assert category.name == 'Salário'
    assert category.type == Category.INCOME
    assert category.is_default is True
    assert category.user is None

@pytest.mark.django_db
def test_custom_category_creation():
    """
    Teste de criação de categoria personalizada.
    """
    user = baker.make(CustomUser)
    category = baker.make(Category, user=user, name='Meu Aluguel', type=Category.EXPENSE, is_default=False)
    assert category.user == user
    assert category.name == 'Meu Aluguel'
    assert category.type == Category.EXPENSE
    assert category.is_default is False

@pytest.mark.django_db
def test_category_type_choices_validation():
    """
    Teste de validação das opções de tipo de categoria.
    """
    user = baker.make(CustomUser)
    with pytest.raises(ValidationError):
        category = baker.make(Category, user=user, name='Invalid Type', type='INVALID_TYPE')
        category.full_clean()

@pytest.mark.django_db
def test_category_name_max_length_validation():
    """
    Teste de validação do tamanho máximo do nome da categoria.
    """
    user = baker.make(CustomUser)
    long_name = 'a' * 101
    with pytest.raises(ValidationError):
        category = baker.make(Category, user=user, name=long_name, type=Category.EXPENSE)
        category.full_clean()

@pytest.mark.django_db
def test_category_color_max_length_validation():
    """
    Teste de validação do tamanho máximo da cor da categoria (hex code).
    """
    user = baker.make(CustomUser)
    long_color = '#FFFFFF0' # 8 chars
    with pytest.raises(ValidationError):
        category = baker.make(Category, user=user, name='Cor Longa', type=Category.EXPENSE, color=long_color)
        category.full_clean()

@pytest.mark.django_db
def test_category_user_relationship():
    """
    Teste de relacionamento de categoria com User.
    """
    user = baker.make(CustomUser, email='category_user@example.com')
    category = baker.make(Category, user=user, name='Conta Teste', type=Category.INCOME)
    assert category.user == user
    assert category.user.email == 'category_user@example.com'

@pytest.mark.django_db
def test_category_str_method():
    """
    Teste do método __str__ da categoria.
    """
    user = baker.make(CustomUser)
    category = baker.make(Category, user=user, name='Alimentação', type=Category.EXPENSE)
    assert str(category) == 'Alimentação (Despesa)'

@pytest.mark.django_db
def test_category_is_active_default_value():
    """
    Teste para verificar o valor padrão de is_active.
    """
    user = baker.make(CustomUser)
    category = baker.make(Category, user=user, name='Ativa', type=Category.INCOME)
    assert category.is_active is True


# --- Category View Tests (CRUD) ---

@pytest.mark.django_db
def test_category_list_view_authenticated_access(client, logged_in_user):
    """
    Teste de acesso autenticado à listagem de categorias.
    """
    # Explicitly create a default category since the fixture was removed
    baker.make(Category, is_default=True, user=None, name='Alimentação', type=Category.EXPENSE)
    default_category_count = 1 
    baker.make(Category, user=logged_in_user, _quantity=2) # Custom categories
    response = client.get(reverse('categories:list'))
    assert response.status_code == 200
    assert 'categories/category_list.html' in [t.name for t in response.templates]
    # Should show default categories + user's custom categories
    assert len(response.context['income_categories']) + len(response.context['expense_categories']) >= default_category_count + 2
    assert any(c.is_default for c in response.context['expense_categories'])
    assert any(c.user == logged_in_user for c in response.context['income_categories']) or any(c.user == logged_in_user for c in response.context['expense_categories'])

@pytest.mark.django_db
def test_category_list_view_unauthenticated_access(client):
    """
    Teste de acesso não autenticado à listagem de categorias (deve redirecionar para login).
    """
    client.logout() # Ensure client is unauthenticated
    response = client.get(reverse('categories:list'))
    assert response.status_code == 302 # Redirect
    assert response.url == f"{reverse('users:login')}?next={reverse('categories:list')}"

@pytest.mark.django_db
def test_category_list_view_displays_only_own_and_default_categories(client, logged_in_user, other_user):
    """
    Teste se a listagem de categorias exibe apenas as categorias do usuário logado e as padrão.
    """
    # Explicitly create a default category since the fixture was removed
    baker.make(Category, is_default=True, user=None, name='Alimentação', type=Category.EXPENSE)
    default_category_count = 1
    baker.make(Category, user=logged_in_user, _quantity=2)
    baker.make(Category, user=other_user, _quantity=1) # Category for another user

    response = client.get(reverse('categories:list'))
    assert response.status_code == 200
    assert len(response.context['income_categories']) + len(response.context['expense_categories']) >= default_category_count + 2 # default + 2 custom for logged_in_user
    for category in response.context['income_categories']:
        assert category.user == logged_in_user or category.user is None
    for category in response.context['expense_categories']:
        assert category.user == logged_in_user or category.user is None

@pytest.mark.django_db
def test_category_create_view_authenticated_get(client, logged_in_user):
    """
    Teste GET autenticado para a view de criação de categoria.
    """
    response = client.get(reverse('categories:create'))
    assert response.status_code == 200
    assert 'categories/category_form.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_category_create_view_unauthenticated_get(client):
    """
    Teste GET não autenticado para a view de criação de categoria.
    """
    response = client.get(reverse('categories:create'))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('categories:create')}"

@pytest.mark.django_db
def test_category_create_view_authenticated_post_valid_data(client, logged_in_user):
    """
    Teste POST autenticado com dados válidos para a view de criação de categoria.
    """
    data = {
        'name': 'Nova Categoria Teste',
        'type': Category.INCOME,
        'color': '#FF0000',
    }
    response = client.post(reverse('categories:create'), data, follow=True)
    assert response.status_code == 200 # Redirects to list view
    assert Category.objects.filter(user=logged_in_user, name='Nova Categoria Teste').exists()
    new_category = Category.objects.get(name='Nova Categoria Teste')
    assert new_category.type == Category.INCOME
    assert new_category.is_default is False
    # assert any(m.level == messages.SUCCESS for m in response.context['messages'])

@pytest.mark.django_db
def test_category_create_view_authenticated_post_invalid_data(client, logged_in_user):
    """
    Teste POST autenticado com dados inválidos (nome vazio) para a view de criação de categoria.
    """
    data = {
        'name': '', # Invalid name
        'type': Category.EXPENSE,
        'color': '#00FF00',
    }
    response = client.post(reverse('categories:create'), data)
    assert response.status_code == 200
    assert not Category.objects.filter(user=logged_in_user, name='').exists()
    assert 'categories/category_form.html' in [t.name for t in response.templates]
    assert 'name' in response.context['form'].errors


@pytest.mark.django_db
def test_category_update_view_authenticated_get_own_custom_category(client, logged_in_user, custom_category):
    """
    Teste GET autenticado para editar categoria personalizada própria.
    """
    response = client.get(reverse('categories:edit', kwargs={'pk': custom_category.pk}))
    assert response.status_code == 200
    assert 'categories/category_form.html' in [t.name for t in response.templates]
    assert response.context['form'].instance == custom_category

@pytest.mark.django_db
def test_category_update_view_unauthenticated_get(client, custom_category):
    """
    Teste GET não autenticado para editar categoria.
    """
    client.logout() # Ensure client is unauthenticated
    response = client.get(reverse('categories:edit', kwargs={'pk': custom_category.pk}))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('categories:edit', kwargs={'pk': custom_category.pk})}"

@pytest.mark.django_db
def test_category_update_view_authenticated_get_other_users_custom_category(client, logged_in_user, other_user):
    """
    Teste GET autenticado para editar categoria personalizada de outro usuário (deve retornar 404).
    """
    category_other = baker.make(Category, user=other_user, name='Cat Outra', type=Category.EXPENSE)
    response = client.get(reverse('categories:edit', kwargs={'pk': category_other.pk}))
    assert response.status_code == 404

@pytest.mark.django_db
def test_category_update_view_authenticated_get_default_category(client, logged_in_user):
    """
    Teste GET autenticado para editar categoria padrão (deve retornar 404, não editável).
    """
    default_category_obj = baker.make(Category, is_default=True, user=None, name='Alimentação', type=Category.EXPENSE)
    response = client.get(reverse('categories:edit', kwargs={'pk': default_category_obj.pk}))
    assert response.status_code == 404

@pytest.mark.django_db
def test_category_update_view_authenticated_post_valid_data(client, logged_in_user, custom_category):
    """
    Teste POST autenticado com dados válidos para editar categoria própria.
    """
    data = {
        'name': 'Nome Atualizado',
        'type': custom_category.type, # Type should not be editable via form in view
        'color': '#FFFFF0',
        'is_active': False,
    }
    response = client.post(reverse('categories:edit', kwargs={'pk': custom_category.pk}), data, follow=True)
    assert response.status_code == 200
    custom_category.refresh_from_db()
    assert custom_category.name == 'Nome Atualizado'
    assert custom_category.color == '#FFFFF0'
    assert custom_category.is_active is False
    # assert any(m.level == messages.SUCCESS for m in response.context['messages'])

@pytest.mark.django_db
def test_category_update_view_authenticated_post_invalid_data(client, logged_in_user, custom_category):
    """
    Teste POST autenticado com dados inválidos para editar categoria própria.
    """
    data = {
        'name': '', # Invalid name
        'type': custom_category.type,
        'color': '#123',
    }
    response = client.post(reverse('categories:edit', kwargs={'pk': custom_category.pk}), data)
    assert response.status_code == 200
    custom_category.refresh_from_db()
    assert custom_category.name != '' # Should not be updated
    assert 'name' in response.context['form'].errors


@pytest.mark.django_db
def test_category_delete_view_authenticated_get_own_custom_category(client, logged_in_user, custom_category):
    """
    Teste GET autenticado para deletar categoria própria.
    """
    response = client.get(reverse('categories:delete', kwargs={'pk': custom_category.pk}))
    assert response.status_code == 200
    assert 'categories/category_confirm_delete.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_category_delete_view_unauthenticated_get(client, custom_category):
    """
    Teste GET não autenticado para deletar categoria.
    """
    client.logout() # Ensure client is unauthenticated
    response = client.get(reverse('categories:delete', kwargs={'pk': custom_category.pk}))
    assert response.status_code == 302
    assert response.url == f"{reverse('users:login')}?next={reverse('categories:delete', kwargs={'pk': custom_category.pk})}"

@pytest.mark.django_db
def test_category_delete_view_authenticated_get_other_users_custom_category(client, logged_in_user, other_user):
    """
    Teste GET autenticado para deletar categoria de outro usuário (deve retornar 404).
    """
    category_other = baker.make(Category, user=other_user, name='Cat Outra Delete', type=Category.EXPENSE)
    response = client.get(reverse('categories:delete', kwargs={'pk': category_other.pk}))
    assert response.status_code == 404

@pytest.mark.django_db
def test_category_delete_view_authenticated_get_default_category(client, logged_in_user):
    """
    Teste GET autenticado para deletar categoria padrão (deve retornar 404, não deletável).
    """
    default_category_obj = baker.make(Category, is_default=True, user=None, name='Alimentação', type=Category.EXPENSE)
    response = client.get(reverse('categories:delete', kwargs={'pk': default_category_obj.pk}))
    assert response.status_code == 404

@pytest.mark.django_db
def test_category_delete_view_authenticated_post_own_custom_category(client, logged_in_user, custom_category):
    """
    Teste POST autenticado para deletar categoria própria.
    """
    response = client.post(reverse('categories:delete', kwargs={'pk': custom_category.pk}), follow=True)
    assert response.status_code == 200
    assert not Category.objects.filter(pk=custom_category.pk).exists()
    # assert any(m.level == messages.SUCCESS for m in response.context['messages'])
    assert response.redirect_chain[0][0] == reverse('categories:list')

@pytest.mark.django_db
def test_category_delete_view_with_transactions(client, logged_in_user, custom_category):
    """
    Teste de exclusão de categoria com transações associadas (deve prevenir a exclusão).
    """
    account = baker.make(Account, user=logged_in_user)
    baker.make(Transaction, account=account, category=custom_category, type=custom_category.type, amount=100.00)

    response = client.post(reverse('categories:delete', kwargs={'pk': custom_category.pk}), follow=True)
    assert response.status_code == 200
    assert Category.objects.filter(pk=custom_category.pk).exists() # Category should NOT be deleted
    assert response.redirect_chain[0][0] == reverse('categories:list')
    assert any(m.level == messages.ERROR for m in response.context['messages'])

# --- Form Tests ---

@pytest.mark.django_db
class TestCategoryForm:
    def test_category_form_valid_data(self, logged_in_user):
        """
        Test that the CategoryForm is valid with correct data.
        """
        form = CategoryForm(data={
            'name': 'Nova Categoria',
            'type': Category.EXPENSE,
            'color': '#FFFFFF',
            'is_active': True
        }, user=logged_in_user)
        assert form.is_valid()

    def test_category_form_unique_name_per_user_and_type(self, logged_in_user):
        """
        Test that the CategoryForm raises a validation error for a duplicate name and type for the same user.
        """
        baker.make(Category, user=logged_in_user, name='Aluguel', type=Category.EXPENSE)
        form = CategoryForm(data={
            'name': 'Aluguel',
            'type': Category.EXPENSE,
            'color': '#000000',
            'is_active': True
        }, user=logged_in_user)
        assert not form.is_valid()
        assert 'name' in form.errors
        assert form.errors['name'][0] == 'A category with the name "Aluguel" already exists for this type.'

    def test_category_form_empty_name(self, logged_in_user):
        """
        Test that the CategoryForm is invalid when the name is empty.
        """
        form = CategoryForm(data={
            'name': '',
            'type': Category.INCOME,
            'color': '#111111',
            'is_active': True
        }, user=logged_in_user)
        assert not form.is_valid()
        assert 'name' in form.errors