from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'balance', 'is_active', 'created_at')
    list_filter = ('is_active', 'user', 'created_at')
    search_fields = ('name', 'description', 'user__email')
    readonly_fields = ('balance', 'created_at', 'updated_at')
    list_per_page = 25

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
