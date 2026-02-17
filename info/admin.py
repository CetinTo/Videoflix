from django.contrib import admin
from .models import LegalPage


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    """Admin interface for legal pages"""
    
    list_display = [
        'page_type',
        'title',
        'is_published',
        'last_updated'
    ]
    list_filter = ['page_type', 'is_published']
    search_fields = ['title', 'content']
    readonly_fields = ['last_updated']
    
    fieldsets = (
        ('Page Information', {
            'fields': ('page_type', 'title', 'is_published')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Metadata', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
