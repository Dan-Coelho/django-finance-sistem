from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2',
                'placeholder': 'Digite seu nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2',
                'placeholder': 'Digite seu sobrenome'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2',
                'placeholder': '(00) 00000-0000'
            })
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Simple validation for Brazilian phone format
        if phone and len(phone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')) < 10:
            raise forms.ValidationError('Telefone deve ter pelo menos 10 dígitos.')
        return phone
