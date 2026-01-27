import pytest
from django.core.exceptions import ValidationError
from model_bakery import baker

from users.models import CustomUser
from categories.models import Category

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
    category = baker.make(Category, user=user, name='Invalid Type', type='INVALID_TYPE')
    with pytest.raises(ValidationError):
        category.full_clean()

@pytest.mark.django_db
def test_category_name_max_length_validation():
    """
    Teste de validação do tamanho máximo do nome da categoria.
    """
    user = baker.make(CustomUser)
    long_name = 'a' * 101
    category = baker.make(Category, user=user, name=long_name, type=Category.EXPENSE)
    with pytest.raises(ValidationError):
        category.full_clean()

@pytest.mark.django_db
def test_category_color_max_length_validation():
    """
    Teste de validação do tamanho máximo da cor da categoria (hex code).
    """
    user = baker.make(CustomUser)
    long_color = '#FFFFFF0' # 8 chars
    category = baker.make(Category, user=user, name='Cor Longa', type=Category.EXPENSE, color=long_color)
    with pytest.raises(ValidationError):
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