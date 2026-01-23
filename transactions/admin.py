from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('type', 'amount', 'date', 'account', 'category', 'description', 'created_at')
    list_filter = ('type', 'date', 'account', 'category', 'created_at')
    search_fields = ('description', 'account__name', 'category__name')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    # Fieldsets for better organization
    fieldsets = (
        (None, {
            'fields': ('type', 'amount', 'date', 'account', 'category')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('account', 'category')
