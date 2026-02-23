from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import os
import shutil


def video_upload_path(instance, filename):
    """Generate upload path for videos. Never None to avoid media/videos/None/."""
    vid = getattr(instance, 'pk', None) or getattr(instance, 'id', None)
    if vid is None:
        import uuid
        vid = f'temp_{uuid.uuid4().hex[:8]}'
    return f'videos/{vid}/{filename}'


def thumbnail_upload_path(instance, filename):
    """Generate upload path for thumbnails. Never None."""
    vid = getattr(instance, 'pk', None) or getattr(instance, 'id', None)
    if vid is None:
        import uuid
        vid = f'temp_{uuid.uuid4().hex[:8]}'
    return f'thumbnails/{vid}/{filename}'


def _remove_media_dirs(dirs_to_remove):
    """Remove given dir paths from disk. Ignores OSError."""
    for dir_path in dirs_to_remove:
        if os.path.isdir(dir_path):
            try:
                shutil.rmtree(dir_path)
            except OSError:
                pass


class Category(models.Model):
    """
    Categories for videos (e.g. Action, Drama, Comedy).
    """
    name = models.CharField(_('Name'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True, blank=True)
    description = models.TextField(_('Beschreibung'), blank=True)
    created_at = models.DateTimeField(_('Erstellt am'), auto_now_add=True)

    class Meta:
        verbose_name = _('Kategorie')
        verbose_name_plural = _('Kategorien')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Video(models.Model):
    """
    Haupt-Video-Model
    """
    QUALITY_CHOICES = [
        ('SD', 'Standard Definition (480p)'),
        ('HD', 'High Definition (720p)'),
        ('FHD', 'Full HD (1080p)'),
        ('4K', '4K Ultra HD'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Entwurf'),
        ('processing', 'Wird verarbeitet'),
        ('published', 'Veröffentlicht'),
        ('archived', 'Archiviert'),
    ]

    title = models.CharField(_('Titel'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True, blank=True)
    description = models.TextField(_('Beschreibung'))
    categories = models.ManyToManyField(
        Category,
        related_name='videos',
        verbose_name=_('Kategorien')
    )
    
    original_video = models.FileField(
        _('Original Video'),
        upload_to=video_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv'])],
        help_text='Original hochgeladene Video-Datei'
    )
    
    video_360p = models.FileField(
        _('360p Version'),
        upload_to=video_upload_path,
        blank=True,
        null=True
    )
    video_480p = models.FileField(
        _('480p Version'),
        upload_to=video_upload_path,
        blank=True,
        null=True
    )
    video_720p = models.FileField(
        _('720p Version'),
        upload_to=video_upload_path,
        blank=True,
        null=True
    )
    video_1080p = models.FileField(
        _('1080p Version'),
        upload_to=video_upload_path,
        blank=True,
        null=True
    )
    
    # Thumbnail/Cover
    thumbnail = models.ImageField(
        _('Thumbnail'),
        upload_to=thumbnail_upload_path,
        blank=True,
        null=True
    )
    
    duration = models.IntegerField(
        _('Dauer (Sekunden)'),
        default=0,
        help_text='Dauer des Videos in Sekunden'
    )
    quality = models.CharField(
        _('Qualität'),
        max_length=3,
        choices=QUALITY_CHOICES,
        default='HD'
    )
    file_size = models.BigIntegerField(
        _('Dateigröße (Bytes)'),
        default=0
    )
    
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(
        _('Hervorgehoben'),
        default=False,
        help_text='Als Featured Video auf der Startseite anzeigen'
    )
    published_at = models.DateTimeField(
        _('Veröffentlicht am'),
        blank=True,
        null=True
    )
    
    view_count = models.IntegerField(_('Anzahl Aufrufe'), default=0)
    rating = models.DecimalField(
        _('Bewertung'),
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    
    director = models.CharField(_('Regisseur'), max_length=200, blank=True)
    cast = models.TextField(_('Besetzung'), blank=True, help_text='Komma-getrennte Liste')
    release_year = models.IntegerField(_('Erscheinungsjahr'), blank=True, null=True)
    language = models.CharField(_('Sprache'), max_length=50, default='Deutsch')
    age_rating = models.CharField(
        _('Altersfreigabe'),
        max_length=10,
        choices=[
            ('0', 'FSK 0'),
            ('6', 'FSK 6'),
            ('12', 'FSK 12'),
            ('16', 'FSK 16'),
            ('18', 'FSK 18'),
        ],
        default='0'
    )
    
    created_at = models.DateTimeField(_('Erstellt am'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Aktualisiert am'), auto_now=True)
    
    uploaded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_videos',
        verbose_name=_('Hochgeladen von')
    )

    class Meta:
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if self.original_video and not self.file_size:
            self.file_size = self.original_video.size
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """On delete, remove associated media dirs (videos, thumbnails)."""
        dirs_to_remove = self._collect_media_dirs_to_remove()
        super().delete(*args, **kwargs)
        _remove_media_dirs(dirs_to_remove)

    def _collect_media_dirs_to_remove(self):
        """Return list of unique media dir paths for this video's file fields."""
        dirs_to_remove = []
        media_root = os.path.abspath(settings.MEDIA_ROOT)
        for field in (self.original_video, self.thumbnail, self.video_360p, self.video_480p,
                      self.video_720p, self.video_1080p):
            if field and field.name:
                rel_dir = os.path.dirname(field.name)
                if rel_dir:
                    full_dir = os.path.abspath(os.path.join(media_root, rel_dir))
                    if full_dir.startswith(media_root) and full_dir not in dirs_to_remove:
                        dirs_to_remove.append(full_dir)
        return dirs_to_remove

    @property
    def formatted_duration(self):
        """Return duration formatted (e.g. 1h 23min)."""
        if self.duration:
            hours = self.duration // 3600
            minutes = (self.duration % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}min"
            return f"{minutes}min"
        return "0min"

    @property
    def formatted_file_size(self):
        """Return file size formatted (e.g. 1.5 GB)."""
        if self.file_size:
            size_mb = self.file_size / (1024 * 1024)
            if size_mb > 1024:
                return f"{size_mb / 1024:.2f} GB"
            return f"{size_mb:.2f} MB"
        return "0 MB"

    def increment_view_count(self):
        """Increment view count by 1."""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class VideoComment(models.Model):
    """
    Comments on videos.
    """
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Video')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='video_comments',
        verbose_name=_('Benutzer')
    )
    content = models.TextField(_('Inhalt'))
    created_at = models.DateTimeField(_('Erstellt am'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Aktualisiert am'), auto_now=True)
    is_edited = models.BooleanField(_('Bearbeitet'), default=False)

    class Meta:
        verbose_name = _('Kommentar')
        verbose_name_plural = _('Kommentare')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.video.title}"


class VideoRating(models.Model):
    """
    Ratings for videos (1–5).
    """
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('Video')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='video_ratings',
        verbose_name=_('Benutzer')
    )
    rating = models.IntegerField(
        _('Bewertung'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Bewertung von 1 bis 5 Sternen'
    )
    created_at = models.DateTimeField(_('Erstellt am'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Aktualisiert am'), auto_now=True)

    class Meta:
        verbose_name = _('Bewertung')
        verbose_name_plural = _('Bewertungen')
        unique_together = ['video', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.video.title} ({self.rating}/5)"
