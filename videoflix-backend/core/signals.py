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
    Handle post-save events for the custom User model.

    - Log when a new user is created
    - Log when an existing user is updated
    """
    if created:
        logger.info(f'New user created: {instance.email}')
    else:
        logger.info(f'User updated: {instance.email}')


@receiver(post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    """
    Handle post-delete events for the custom User model.

    - Log the deletion
    - Optionally delete the profile picture from disk
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

def _should_enqueue_video_processing(instance, created):
    """
    Decide whether the video processing job should be enqueued.

    Rules:
    - New `Video` instance with an `original_video` → enqueue
    - Existing `Video` that just received an `original_video` while still in `draft` → enqueue
    - Do NOT enqueue when the status is not `draft` (already processing or published)
    """
    if not instance.original_video:
        return False
    if created:
        return True
    # Only trigger again while the video is still in draft
    # (e.g. when an original file is uploaded later).
    if instance.status != 'draft':
        return False
    if instance.video_360p:
        return False
    return True


@receiver(post_save, sender='videos.Video')
def auto_process_video(sender, instance, created, **kwargs):
    """
    Post-save signal for the `Video` model.

    It queues the asynchronous processing task (duration, thumbnail, HLS conversion)
    via Django-RQ when:
    - a new video with an `original_video` is created, or
    - an existing draft video receives an `original_video` and has not been processed yet.
    """
    if not _should_enqueue_video_processing(instance, created):
        return

    logger.info(f'Video upload/update: {instance.title} (ID {instance.id}) – starting processing in queue')

    # Import here to avoid circular imports
    from videos.tasks import process_uploaded_video

    # Enqueue the job without extra kwargs so RQ does not pass
    # unexpected keyword arguments into `process_uploaded_video`.
    queue = django_rq.get_queue('default')
    queue.enqueue(process_uploaded_video, instance.id)
    logger.info(f'Video processing queued for video ID {instance.id}')
