# conftest.py
import pytest

pytest_plugins = ["pytest_django"]

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # You can add setup logic here if needed, e.g. for initial data
        pass