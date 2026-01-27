from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
    UserCreationForm,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import CustomUser


class SignUpForm(UserCreationForm):
    """
    Form for user registration that collects email and password information.
    """
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'email@exemplo.com'
        }),
        help_text='Digite seu endereço de e-mail.'
    )
    password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'Digite sua senha'
        }),
        help_text='Sua senha deve conter pelo menos 8 caracteres e não pode ser muito comum.'
    )
    password2 = forms.CharField(
        label="Confirmação de senha",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'Confirme sua senha'
        }),
        strip=False,
        help_text='Digite a mesma senha para verificação.'
    )

    class Meta:
        model = CustomUser
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'email@exemplo.com'
            })
        }

    def clean_email(self):
        """
        Validate that the email is unique (case-insensitive).
        """
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este e-mail já está sendo utilizado.")
        return email

    def clean_password2(self):
        """
        Validate that the two password fields match.
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("As senhas não coincidem.")
        return password2

    def _post_clean(self):
        """
        Run password validation after cleaning the data.
        """
        super()._post_clean()
        password = self.cleaned_data.get('password1')
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password1', error)

    def save(self, commit=True):
        """
        Save the user with the provided email and password.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Form for user login that authenticates using email and password.
    """
    username = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'email@exemplo.com'
        }),
        help_text='Digite seu endereço de e-mail.'
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'Digite sua senha'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
        }),
        label="Lembrar-me"
    )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and customize field labels.
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Email"


class EmailChangeForm(forms.ModelForm):
    """
    A form for changing a user's email address.
    """
    email = forms.EmailField(
        label="Novo email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'novoemail@exemplo.com'
        })
    )
    password = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
            'placeholder': 'Digite sua senha atual para confirmar'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este e-mail já está sendo utilizado por outra conta.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise ValidationError("A senha atual está incorreta.")
        return password

    def save(self, commit=True):
        self.user.email = self.cleaned_data['email']
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(DjangoPasswordChangeForm):
    """
    A password change form with updated styling.
    """
    old_password = forms.CharField(
        label="Senha antiga",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    new_password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
        })
    )
    new_password2 = forms.CharField(
        label="Confirmação da nova senha",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
        })
    )