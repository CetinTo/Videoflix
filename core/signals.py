"""
Django Signals for Videoflix Project
Central management of all signals
"""
import django_rq
import logging
import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


# ================================
# USER SIGNALS
# ================================

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal triggered after a User is saved
    """
    if created:
        logger.info(f'New user created: {instance.email}')
    else:
        logger.info(f'User updated: {instance.email}')


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    """
    Signal triggered after a User is deleted
    """
    logger.info(f'User deleted: {instance.email} (ID: {instance.id})')
    
    # Optional: Delete profile picture if exists
    if hasattr(instance, 'profile_picture') and instance.profile_picture:
        if os.path.isfile(instance.profile_picture.path):
            os.remove(instance.profile_picture.path)
            logger.info(f'Profile picture deleted for user: {instance.email}')


# ================================
# VIDEO SIGNALS
# ================================

@receiver(post_save, sender='videos.Video')
def auto_process_video(sender, instance, created, **kwargs):
    """
    Signal: Automatically starts video processing after upload
    
    Triggered when a new video is created
    """
    if created and instance.original_video:
        logger.info(f'New video uploaded: {instance.title}')
        logger.info('Starting video processing in queue')
        
        # Import here to avoid circular imports
        from videos.tasks import process_uploaded_video
        
        # Add video processing to RQ queue
        queue = django_rq.get_queue('default')
        queue.enqueue(
            process_uploaded_video,
            instance.id,
            timeout='1h',  # Max. 1 hour for processing
            result_ttl=86400  # Keep result for 24 hours
        )
        
        logger.info(f'Video processing queued for video ID {instance.id}')
