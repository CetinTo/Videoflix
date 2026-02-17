from django.db import models


class LegalPage(models.Model):
    """Model for legal pages (Privacy Policy, Imprint, Terms of Service)"""
    
    PAGE_TYPE_CHOICES = [
        ('privacy', 'Privacy Policy'),
        ('imprint', 'Imprint'),
        ('terms', 'Terms of Service'),
    ]
    
    page_type = models.CharField(
        max_length=20,
        choices=PAGE_TYPE_CHOICES,
        unique=True,
        help_text='Type of legal page'
    )
    title = models.CharField(
        max_length=200,
        help_text='Page title'
    )
    content = models.TextField(
        help_text='Page content in HTML format'
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )
    is_published = models.BooleanField(
        default=True,
        help_text='Whether the page is published'
    )
    
    class Meta:
        verbose_name = 'Legal Page'
        verbose_name_plural = 'Legal Pages'
        ordering = ['page_type']
    
    def __str__(self):
        return f"{self.get_page_type_display()}"
