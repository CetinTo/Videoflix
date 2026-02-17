from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User Model for Videoflix
    Extends the default Django User Model
    """
    # Username is automatically generated from email
    username = models.CharField(_('Username'), max_length=150, unique=True, blank=True)
    email = models.EmailField(_('Email Address'), unique=True)
    phone = models.CharField(_('Phone Number'), max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(
        _('Profile Picture'),
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    birth_date = models.DateField(_('Birth Date'), blank=True, null=True)
    subscription_type = models.CharField(
        _('Subscription Type'),
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('basic', 'Basic'),
            ('premium', 'Premium'),
        ],
        default='free'
    )
    is_email_verified = models.BooleanField(_('Email Verified'), default=False)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    # For email login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def save(self, *args, **kwargs):
        """Generate username automatically from email if not set"""
        if not self.username:
            # Take the part before @ from email as username
            base_username = self.email.split('@')[0]
            username = base_username
            
            # If username already exists, add number
            counter = 1
            while User.objects.filter(username=username).exclude(pk=self.pk).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            self.username = username
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Returns the full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def has_premium_subscription(self):
        """Checks if the user has a premium subscription"""
        return self.subscription_type == 'premium'


class UserWatchHistory(models.Model):
    """
    Stores the watch history of a user
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='watch_history',
        verbose_name=_('User')
    )
    video = models.ForeignKey(
        'videos.Video',
        on_delete=models.CASCADE,
        related_name='watch_records',
        verbose_name=_('Video')
    )
    watched_at = models.DateTimeField(_('Watched At'), auto_now_add=True)
    progress = models.IntegerField(
        _('Progress (Seconds)'),
        default=0,
        help_text='How many seconds of the video were watched'
    )
    completed = models.BooleanField(_('Completed'), default=False)

    class Meta:
        verbose_name = _('Watch History')
        verbose_name_plural = _('Watch Histories')
        ordering = ['-watched_at']
        unique_together = ['user', 'video']

    def __str__(self):
        return f"{self.user.email} - {self.video.title}"


class UserFavorite(models.Model):
    """
    Stores the favorites of a user
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('User')
    )
    video = models.ForeignKey(
        'videos.Video',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name=_('Video')
    )
    added_at = models.DateTimeField(_('Added At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')
        ordering = ['-added_at']
        unique_together = ['user', 'video']

    def __str__(self):
        return f"{self.user.email} - {self.video.title}"
