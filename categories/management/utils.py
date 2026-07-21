from django.contrib.auth import get_user_model

def create_default_categories(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')
    User = get_user_model()

    # Income categories
    income_categories = [
        {'name': 'Salário', 'color': '#4CAF50', 'type': 'INCOME'},
        {'name': 'Freelance', 'color': '#8BC34A', 'type': 'INCOME'},
        {'name': 'Investimentos', 'color': '#CDDC39', 'type': 'INCOME'},
        {'name': 'Outros', 'color': '#FFEB3B', 'type': 'INCOME'},
    ]

    # Expense categories
    expense_categories = [
        {'name': 'Alimentação', 'color': '#F44336', 'type': 'EXPENSE'},
        {'name': 'Transporte', 'color': '#E91E63', 'type': 'EXPENSE'},
        {'name': 'Moradia', 'color': '#9C27B0', 'type': 'EXPENSE'},
        {'name': 'Saúde', 'color': '#673AB7', 'type': 'EXPENSE'},
        {'name': 'Lazer', 'color': '#3F51B5', 'type': 'EXPENSE'},
        {'name': 'Educação', 'color': '#2196F3', 'type': 'EXPENSE'},
        {'name': 'Outros', 'color': '#03A9F4', 'type': 'EXPENSE'},
    ]

    # Create income categories
    for cat_data in income_categories:
        Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'color': cat_data['color'],
                'type': cat_data['type'],
                'is_default': True,
                'is_active': True,
                'user': None
            }
        )

    # Create expense categories
    for cat_data in expense_categories:
        Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'color': cat_data['color'],
                'type': cat_data['type'],
                'is_default': True,
                'is_active': True,
                'user': None
            }
        )


def reverse_default_categories(apps, schema_editor):
    Category = apps.get_model('categories', 'Category')

    # Delete all default categories
    Category.objects.filter(is_default=True).delete()