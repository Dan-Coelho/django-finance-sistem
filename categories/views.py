import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import CategoryForm
from .models import Category

logger = logging.getLogger(__name__)

@login_required
def category_list(request):
    # Cache for default categories
    default_categories = cache.get('default_categories')
    if not default_categories:
        default_categories = Category.objects.filter(is_default=True)
        cache.set('default_categories', default_categories, 3600)  # Cache for 1 hour

    # Get user-specific categories
    user_categories = Category.objects.filter(user=request.user)

    # Combine querysets
    all_categories = default_categories | user_categories
    all_categories = all_categories.select_related('user').order_by('type', 'name')

    # Separate income and expense categories
    income_categories = all_categories.filter(type='INCOME')
    expense_categories = all_categories.filter(type='EXPENSE')

    # Apply filters if present
    category_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')

    if category_type:
        if category_type == 'INCOME':
            income_categories = income_categories.filter(type='INCOME')
            expense_categories = expense_categories.none()  # Use none() for empty queryset
        elif category_type == 'EXPENSE':
            expense_categories = expense_categories.filter(type='EXPENSE')
            income_categories = income_categories.none()

    if search_query:
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
        response = super().form_valid(form)
        messages.success(self.request, 'Categoria criada com sucesso!')
        logger.info(f"Category '{form.instance.name}' created by user '{self.request.user}'.")
        return response

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

        response = super().form_valid(form)
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        logger.info(f"Category '{form.instance.name}' updated by user '{self.request.user}'.")
        return response

    def get_queryset(self):
        # Only allow updating categories that belong to the current user and are not default
        return Category.objects.filter(user=self.request.user, is_default=False).select_related('user')

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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        category = self.object

        if category.user != request.user or category.is_default:
            messages.error(request, 'Você não pode excluir esta categoria.')
            return redirect('categories:list')

        if category.transactions.exists():
            messages.error(request, f'Não é possível excluir a categoria "{category.name}" porque ela está sendo usada em transações.')
            return redirect('categories:list')

        category_name = category.name
        messages.success(request, 'Categoria excluída com sucesso!')
        logger.info(f"Category '{category_name}' deleted by user '{request.user}'.")
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        # Only allow deleting categories that belong to the current user and are not default
        return Category.objects.filter(user=self.request.user, is_default=False).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [
            {'title': 'Categorias', 'url': reverse_lazy('categories:list')},
            {'title': 'Excluir Categoria', 'active': True}
        ]
        return context
