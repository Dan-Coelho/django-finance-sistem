import pytest
from model_bakery import baker

from users.models import CustomUser
from profiles.models import Profile

@pytest.mark.django_db
def test_profile_creation_on_user_creation():
    """
    Teste de criação automática de Profile via signal.
    """
    user = baker.make(CustomUser, email='newuser@example.com', password='testpassword')
    profile = Profile.objects.get(user=user)
    assert profile is not None
    assert profile.user == user

@pytest.mark.django_db
def test_profile_user_relationship():
    """
    Teste de relacionamento OneToOne entre Profile e User.
    """
    user = baker.make(CustomUser, email='anotheruser@example.com', password='testpassword')
    profile = user.profile
    assert profile.user.email == 'anotheruser@example.com'
    assert profile.user == user

@pytest.mark.django_db
def test_profile_str_method():
    """
    Teste do método __str__ do Profile.
    """
    user = baker.make(CustomUser, email='profile_str@example.com')
    profile = user.profile
    assert str(profile) == f"{user.email}'s Profile"

@pytest.mark.django_db
def test_profile_fields_default_values():
    """
    Teste para verificar os valores padrão dos campos do Profile.
    """
    user = baker.make(CustomUser, email='defaultprofile@example.com')
    profile = user.profile
    assert profile.first_name == ''
    assert profile.last_name == ''
    assert profile.phone == ''
    assert profile.created_at is not None
    assert profile.updated_at is not None