from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from profiles.models import Profile

from .models import CustomUser


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    # Define the fields to use for the User creation form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    # Campos a serem exibidos na lista de usuários
    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'created_at')

    # Campos pelos quais será possível pesquisar
    search_fields = ('email',)

    # Campos pelos quais será possível filtrar
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')

    # Campos a serem exibidos no formulário de edição
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    # Campos somente leitura
    readonly_fields = ('created_at', 'updated_at', 'last_login')

    # Define ordering to avoid the username reference error
    ordering = ('email',)

    # Adiciona o inline do perfil
    inlines = (ProfileInline,)


admin.site.register(CustomUser, CustomUserAdmin)
