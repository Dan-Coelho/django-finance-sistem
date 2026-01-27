from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ProfileForm
from .models import Profile


@login_required
def profile_detail(request):
    """
    View to display the user's profile information
    """
    profile, created = Profile.objects.select_related('user').get_or_create(user=request.user)

    # Calculate statistics
    from accounts.models import Account
    from transactions.models import Transaction

    total_transactions = Transaction.objects.filter(account__user=request.user).count()
    total_accounts = Account.objects.filter(user=request.user).count()

    context = {
        'profile': profile,
        'total_transactions': total_transactions,
        'total_accounts': total_accounts,
        'breadcrumb_items': [
            {'title': 'Perfil', 'active': True}
        ]
    }
    return render(request, 'profiles/profile_detail.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View to update the user's profile information.
    """
    form_class = ProfileForm
    template_name = 'profiles/profile_form.html'
    success_url = reverse_lazy('profiles:detail')

    def get_object(self, queryset=None):
        # Get or create the profile for the current user
        profile, created = Profile.objects.select_related('user').get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        context['breadcrumb_items'] = [
            {'title': 'Perfil', 'url': reverse_lazy('profiles:detail')},
            {'title': 'Editar Perfil', 'active': True}
        ]
        return context
