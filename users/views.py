from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .forms import SignUpForm, LoginForm


User = get_user_model()


class SignUpView(CreateView):
    """
    View for user registration that handles the signup form and creates a new user.
    """
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('dashboard')  # Redirect to dashboard after successful signup

    def form_valid(self, form):
        """
        Override form_valid to log the user in automatically after successful registration.
        """
        user = form.save()
        login(self.request, user)  # Log the user in automatically after signup
        messages.success(self.request, 'Conta criada com sucesso! Bem-vindo ao nosso sistema.')
        return redirect(self.success_url)

    def form_invalid(self, form):
        """
        Override form_invalid to show error messages when form is invalid.
        """
        messages.error(self.request, 'Por favor, corrija os erros abaixo.')
        return super().form_invalid(form)


class LoginView(LoginView):
    """
    View for user login that handles authentication.
    """
    form_class = LoginForm
    template_name = 'registration/login.html'
    next_page = reverse_lazy('dashboard')  # Redirect to dashboard after successful login

    def form_valid(self, form):
        """
        Override form_valid to handle the 'remember-me' functionality.
        """
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # Set session expiry to 0 (session expires when browser closes)
            self.request.session.set_expiry(0)

        messages.success(self.request, f'Bem-vindo de volta, {form.get_user().email}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Override form_invalid to show error messages when login fails.
        """
        messages.error(self.request, 'Email ou senha inválidos. Por favor, tente novamente.')
        return super().form_invalid(form)


class LogoutView(LogoutView):
    """
    View for user logout that handles the logout process.
    """
    next_page = reverse_lazy('landing_page')  # Redirect to landing page after logout

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to show a confirmation message after logout.
        """
        if request.user.is_authenticated:
            messages.info(request, 'Você saiu da sua conta com sucesso. Até logo!')
        return super().dispatch(request, *args, **kwargs)


def landing_page(request):
    """
    View for the landing page that redirects authenticated users to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')
