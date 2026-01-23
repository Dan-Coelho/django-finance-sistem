from django.contrib import admin
from django.utils.html import format_html
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'get_color_display', 'is_default', 'is_active', 'user', 'created_at')
    list_filter = ('type', 'is_default', 'is_active', 'user', 'created_at')
    search_fields = ('name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    def get_color_display(self, obj):
        return format_html(
            '<span style="display:inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></span> {}',
            obj.color,
            obj.color
        )
    get_color_display.short_description = 'Color'

    # Customize form layout
    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'color', 'is_active')
        }),
        ('User Information', {
            'fields': ('user', 'is_default'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Category)
class CategoryAdminWithPreview(CategoryAdmin):
    pass
