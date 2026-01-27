import pytest
from django.db.utils import IntegrityError
from model_bakery import baker

from users.models import CustomUser

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