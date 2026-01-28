from categories.management.utils import create_default_categories, reverse_default_categories
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, reverse_default_categories),
    ]
