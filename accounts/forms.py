from django import forms
from django.core.exceptions import ValidationError
from .models import Account

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'description', 'balance']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'Nome da conta'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Descrição da conta'
            }),
            'balance': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }
    
    def clean_balance(self):
        balance = self.cleaned_data.get('balance')
        if balance is not None and balance < 0:
            raise ValidationError('O saldo não pode ser negativo.')
        return balance
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or name.strip() == '':
            raise ValidationError('O nome da conta é obrigatório.')
        return name