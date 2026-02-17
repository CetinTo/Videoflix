from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Category, Video, VideoComment, VideoRating


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin-Konfiguration für Kategorien"""
    
    list_display = ['name', 'slug', 'video_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    def video_count(self, obj):
        """Zeigt die Anzahl der Videos in dieser Kategorie"""
        return obj.videos.count()
    video_count.short_description = 'Anzahl Videos'


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin-Konfiguration für Videos"""
    
    list_display = [
        'title',
        'status',
        'quality',
        'duration_display',
        'view_count',
        'rating',
        'is_featured',
        'created_at'
    ]
    list_filter = ['status', 'quality', 'is_featured', 'categories', 'age_rating', 'created_at']
    search_fields = ['title', 'description', 'director', 'cast']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['categories']
    readonly_fields = ['view_count', 'file_size', 'created_at', 'updated_at', 'thumbnail_preview']
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Basis-Informationen'), {
            'fields': ('title', 'slug', 'description', 'categories')
        }),
        (_('Video-Dateien'), {
            'fields': (
                'original_video',
                'video_360p',
                'video_480p',
                'video_720p',
                'video_1080p',
                'thumbnail',
                'thumbnail_preview'
            )
        }),
        (_('Metadaten'), {
            'fields': (
                'duration',
                'quality',
                'file_size',
                'director',
                'cast',
                'release_year',
                'language',
                'age_rating'
            )
        }),
        (_('Status & Veröffentlichung'), {
            'fields': ('status', 'is_featured', 'published_at', 'uploaded_by')
        }),
        (_('Statistiken'), {
            'fields': ('view_count', 'rating')
        }),
        (_('Zeitstempel'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Formatierte Anzeige der Dauer"""
        return obj.formatted_duration
    duration_display.short_description = 'Dauer'
    
    def thumbnail_preview(self, obj):
        """Zeigt eine Vorschau des Thumbnails"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />',
                obj.thumbnail.url
            )
        return _('Kein Thumbnail')
    thumbnail_preview.short_description = 'Thumbnail Vorschau'


@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    """Admin-Konfiguration für Kommentare"""
    
    list_display = ['user', 'video', 'content_preview', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at']
    search_fields = ['user__email', 'video__title', 'content']
    raw_id_fields = ['user', 'video']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        """Zeigt eine Vorschau des Kommentars"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Inhalt'


@admin.register(VideoRating)
class VideoRatingAdmin(admin.ModelAdmin):
    """Admin-Konfiguration für Bewertungen"""
    
    list_display = ['user', 'video', 'rating', 'rating_stars', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__email', 'video__title']
    raw_id_fields = ['user', 'video']
    ordering = ['-created_at']
    
    def rating_stars(self, obj):
        """Zeigt die Bewertung als Sterne"""
        stars = '⭐' * obj.rating
        return format_html(stars)
    rating_stars.short_description = 'Sterne'
