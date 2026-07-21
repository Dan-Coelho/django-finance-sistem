from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from accounts.models import Account
from categories.models import Category


class Transaction(models.Model):
    """
    Represents a financial transaction, which can be either income or an expense.
    """
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'

    TYPE_CHOICES = [
        (INCOME, 'Receita'),
        (EXPENSE, 'Despesa'),
    ]

    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]  # amount > 0
    )
    date = models.DateField(default=timezone.localdate)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Custom validation for the transaction model.
        """
        super().clean()

        # Validate amount > 0
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({'amount': 'Amount must be greater than 0.'})

        # Validate date is not in the future
        if self.date and self.date > timezone.now().date(): # self.date is already a date object. If it were datetime, convert to date.
            raise ValidationError({'date': 'Date cannot be in the future.'})

        # Validate category.type matches transaction.type
        if self.category and self.type != self.category.type:
            raise ValidationError({
                'category': f'Category type ({self.category.get_type_display()}) must match transaction type ({self.get_type_display()}).'
            })

    def save(self, *args, **kwargs):
        """
        Overrides the save method to call full_clean before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} - {self.date}"

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['account']),
            models.Index(fields=['category']),
            models.Index(fields=['date', 'account']),
            models.Index(fields=['date', 'category']),
        ]
