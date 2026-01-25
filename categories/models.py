from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'

    TYPE_CHOICES = [
        (INCOME, 'Receita'),
        (EXPENSE, 'Despesa'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#000000')  # Hex color code
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=EXPENSE)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
