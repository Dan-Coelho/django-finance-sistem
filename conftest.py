# conftest.py
import pytest
from django.apps import apps
from django.db import connection

pytest_plugins = ["pytest_django"]

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # Ensure that the create_default_categories function from the migration is run
        # This simulates running the 0002_create_default_categories.py migration
        from categories.management.utils import create_default_categories
        create_default_categories(apps, connection.schema_editor())
