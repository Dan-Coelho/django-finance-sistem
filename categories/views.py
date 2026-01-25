from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import CategoryForm
from .models import Category


@login_required
def category_list(request):
    # Get categories for the current user plus default categories
    user_categories = Category.objects.filter(
        Q(user=request.user) | Q(is_default=True)
    ).order_by('type', 'name')

    # Separate income and expense categories
    income_categories = user_categories.filter(type='INCOME')
    expense_categories = user_categories.filter(type='EXPENSE')

    # Apply filters if present
    category_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')

    if category_type:
        user_categories = user_categories.filter(type=category_type)
        if category_type == 'INCOME':
            income_categories = user_categories
            expense_categories = []
        elif category_type == 'EXPENSE':
            expense_categories = user_categories
            income_categories = []

    if search_query:
        user_categories = user_categories.filter(name__icontains=search_query)
        income_categories = income_categories.filter(name__icontains=search_query)
        expense_categories = expense_categories.filter(name__icontains=search_query)

    context = {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
        'category_type': category_type,
        'search_query': search_query,
        'breadcrumb_items': [
            {'title': 'Categorias', 'active': True}
        ]
    }
    return render(request, 'categories/category_list.html', context)


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_default = False
        messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Categorias', 'url': reverse_lazy('categories:list')},
            {'title': 'Nova Categoria', 'active': True}
        ]
        return context


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_url = reverse_lazy('categories:list')

    def form_valid(self, form):
        # Ensure the category belongs to the current user and is not a default
        category = self.get_object()
        if category.user != self.request.user or category.is_default:
            messages.error(self.request, 'Você não pode editar esta categoria.')
            return redirect('categories:list')

        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)

    def get_queryset(self):
        # Only allow updating categories that belong to the current user and are not default
        return Category.objects.filter(user=self.request.user, is_default=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Categorias', 'url': reverse_lazy('categories:list')},
            {'title': 'Editar Categoria', 'active': True}
        ]
        return context


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('categories:list')

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        if category.user != request.user or category.is_default:
            messages.error(request, 'Você não pode excluir esta categoria.')
            return redirect('categories:list')

        # Check if there are transactions using this category
        if category.transaction_set.exists():
            messages.error(request, f'Não é possível excluir a categoria "{category.name}" porque ela está sendo usada em transações.')
            return redirect('categories:list')

        messages.success(request, 'Categoria excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        # Only allow deleting categories that belong to the current user and are not default
        return Category.objects.filter(user=self.request.user, is_default=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Categorias', 'url': reverse_lazy('categories:list')},
            {'title': 'Excluir Categoria', 'active': True}
        ]
        return context
