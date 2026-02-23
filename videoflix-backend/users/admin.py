from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserWatchHistory, UserFavorite


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin-Konfiguration für Custom User Model"""
    
    list_display = ['email', 'username', 'full_name', 'subscription_type', 'is_email_verified', 'is_active', 'created_at']
    list_filter = ['subscription_type', 'is_email_verified', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Persönliche Informationen'), {'fields': ('username', 'first_name', 'last_name', 'phone', 'birth_date', 'profile_picture')}),
        (_('Abo-Informationen'), {'fields': ('subscription_type',)}),
        (_('Berechtigungen'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_email_verified', 'groups', 'user_permissions'),
        }),
        (_('Wichtige Daten'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(UserWatchHistory)
class UserWatchHistoryAdmin(admin.ModelAdmin):
    """Admin-Konfiguration für Wiedergabe-Historie"""
    
    list_display = ['user', 'video', 'progress', 'completed', 'watched_at']
    list_filter = ['completed', 'watched_at']
    search_fields = ['user__email', 'video__title']
    ordering = ['-watched_at']
    raw_id_fields = ['user', 'video']


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    """Admin-Konfiguration für Favoriten"""
    
    list_display = ['user', 'video', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__email', 'video__title']
    ordering = ['-added_at']
    raw_id_fields = ['user', 'video']
