from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Account, Category, Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'category', 'account', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 text-gray-900',
                'step': 'any',
                'placeholder': '0.00'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 text-gray-900'
            }),
            'category': forms.Select(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 text-gray-900'
            }),
            'account': forms.Select(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 text-gray-900'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 text-gray-900',
                'placeholder': 'Descrição da transação...'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        transaction_type = kwargs.pop('transaction_type', None)  # Extract transaction type
        super().__init__(*args, **kwargs)

        if user:
            # Filter accounts for the current user
            self.fields['account'].queryset = Account.objects.filter(user=user)

            # Filter categories based on transaction type
            if transaction_type:
                self.fields['category'].queryset = Category.objects.filter(
                    Q(user=user) | Q(is_default=True),
                    type=transaction_type
                ).order_by('name')
            else:
                # If no type specified, use the instance's type or show all
                if self.instance and self.instance.pk:
                    self.fields['category'].queryset = Category.objects.filter(
                        Q(user=user) | Q(is_default=True),
                        type=self.instance.type
                    ).order_by('name')
                else:
                    # For new transactions, we'll set this in the view
                    self.fields['category'].queryset = Category.objects.none()

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError('O valor deve ser maior que zero.')
        return amount

    def clean_date(self):
        date = self.cleaned_data.get('date')
        from datetime import date as dt
        if date and date > dt.today():
            raise ValidationError('A data não pode ser futura.')
        return date

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        transaction_type = cleaned_data.get('type')

        # Validate that category type matches transaction type
        if category and transaction_type and category.type != transaction_type:
            raise ValidationError('A categoria deve ser do mesmo tipo da transação.')

        return cleaned_data


class TransactionFilterForm(forms.Form):
    TYPE_CHOICES = [
        ('all', 'Todos'),
        ('INCOME', 'Receita'),
        ('EXPENSE', 'Despesa'),
    ]

    account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md bg-gray-600'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md bg-gray-600'
        })
    )
    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md bg-gray-600'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md bg-gray-600'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md bg-gray-600'
        })
    )
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar...',
            'class': 'mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md bg-gray-600'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['account'].queryset = Account.objects.filter(user=user)
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(is_default=True)
            ).order_by('type', 'name')
