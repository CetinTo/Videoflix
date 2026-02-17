from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import os


def video_upload_path(instance, filename):
    """Generiert Upload-Pfad für Videos"""
    return f'videos/{instance.id}/{filename}'


def thumbnail_upload_path(instance, filename):
    """Generiert Upload-Pfad für Thumbnails"""
    return f'thumbnails/{instance.id}/{filename}'


class Category(models.Model):
    """
    Kategorien für Videos (z.B. Action, Drama, Komödie)
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

    # Basis-Informationen
    title = models.CharField(_('Titel'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True, blank=True)
    description = models.TextField(_('Beschreibung'))
    categories = models.ManyToManyField(
        Category,
        related_name='videos',
        verbose_name=_('Kategorien')
    )
    
    # Video-Dateien
    original_video = models.FileField(
        _('Original Video'),
        upload_to=video_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv'])],
        help_text='Original hochgeladene Video-Datei'
    )
    
    # Konvertierte Versionen (werden automatisch generiert)
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
    
    # Video-Metadaten
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
    
    # Status und Veröffentlichung
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
    
    # Statistiken
    view_count = models.IntegerField(_('Anzahl Aufrufe'), default=0)
    rating = models.DecimalField(
        _('Bewertung'),
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)]
    )
    
    # Zusätzliche Informationen
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
    
    # Zeitstempel
    created_at = models.DateTimeField(_('Erstellt am'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Aktualisiert am'), auto_now=True)
    
    # Hochgeladen von
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
        
        # Dateigröße automatisch setzen
        if self.original_video and not self.file_size:
            self.file_size = self.original_video.size
        
        super().save(*args, **kwargs)

    @property
    def formatted_duration(self):
        """Gibt die Dauer formatiert zurück (z.B. 1h 23min)"""
        if self.duration:
            hours = self.duration // 3600
            minutes = (self.duration % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}min"
            return f"{minutes}min"
        return "0min"

    @property
    def formatted_file_size(self):
        """Gibt die Dateigröße formatiert zurück (z.B. 1.5 GB)"""
        if self.file_size:
            size_mb = self.file_size / (1024 * 1024)
            if size_mb > 1024:
                return f"{size_mb / 1024:.2f} GB"
            return f"{size_mb:.2f} MB"
        return "0 MB"

    def increment_view_count(self):
        """Erhöht die Anzahl der Aufrufe um 1"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class VideoComment(models.Model):
    """
    Kommentare zu Videos
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
    Bewertungen für Videos
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
