"""
Video Processing Tasks mit Django-RQ
Verwendet ffmpeg zur Video-Konvertierung in verschiedene Qualitäten
"""
import os
import logging
from django.conf import settings
from .models import Video
from .utils import (
    get_video_by_id,
    get_original_video_path,
    get_output_path,
    get_quality_settings,
    build_ffmpeg_command,
    build_hls_ffmpeg_command,
    run_ffmpeg_command,
    save_video_file,
    get_video_duration_seconds,
    create_hls_directory,
    build_thumbnail_command,
    save_thumbnail_file,
    update_video_duration
)

logger = logging.getLogger(__name__)


def _ensure_video_and_input_path(video_id):
    """Return (video, input_path) or (None, None) if video/input missing."""
    video = get_video_by_id(video_id)
    if not video:
        return None, None
    input_path = get_original_video_path(video)
    if not input_path:
        logger.error(f'Original video file not found for {video.title} (id={video_id})')
        return None, None
    return video, input_path


def convert_video_to_quality(video_id, resolution='720p'):
    """Convert video to specific quality"""
    video, input_path = _ensure_video_and_input_path(video_id)
    if not video:
        return False
    logger.info(f'Start conversion for {video.title} to {resolution}')
    output_path = get_output_path(input_path, f'{resolution}.mp4')
    quality_settings = get_quality_settings(resolution)
    command = build_ffmpeg_command(input_path, output_path, quality_settings)
    success, error = run_ffmpeg_command(command)
    if success:
        _save_converted_video(video, resolution, output_path)
        logger.info(f'Video {resolution} saved for {video.title}')
        return True
    logger.error(f'FFmpeg error: {error}')
    return False


def _save_converted_video(video, resolution, file_path):
    """Save converted video to model field"""
    field_name = f'video_{resolution}'
    save_video_file(video, field_name, file_path)


def generate_thumbnail(video_id, timestamp='00:00:05'):
    """Generate video thumbnail at specific timestamp"""
    video, input_path = _ensure_video_and_input_path(video_id)
    if not video:
        return False
    logger.info(f'Generate thumbnail for {video.title}')
    thumbnail_path = get_output_path(input_path, 'thumbnail.jpg')
    command = build_thumbnail_command(input_path, thumbnail_path, timestamp)
    success, error = run_ffmpeg_command(command)
    if success:
        save_thumbnail_file(video, thumbnail_path)
        logger.info(f'Thumbnail saved for {video.title}')
        return True
    logger.error(f'FFmpeg error: {error}')
    return False


def get_video_duration(video_id):
    """Get video duration using ffprobe"""
    video, input_path = _ensure_video_and_input_path(video_id)
    if not video:
        return False
    logger.info(f'Get duration for {video.title} from {input_path}')
    duration_seconds = get_video_duration_seconds(input_path)
    if duration_seconds > 0:
        update_video_duration(video, duration_seconds)
        logger.info(f'Duration saved: {duration_seconds} seconds')
        return True
    logger.error(f'Could not determine video duration (ffprobe returned 0 for {input_path})')
    return False


def convert_video_to_hls(video_id, resolution='720p'):
    """Convert video to HLS format with M3U8 playlist and TS segments"""
    video, input_path = _ensure_video_and_input_path(video_id)
    if not video:
        return False
    logger.info(f'Start HLS conversion for {video.title} to {resolution}')
    output_dir = os.path.dirname(input_path)
    hls_dir = create_hls_directory(output_dir, resolution)
    quality_settings = get_quality_settings(resolution)
    command = build_hls_ffmpeg_command(input_path, hls_dir, quality_settings)
    success, error = run_ffmpeg_command(command)
    if success:
        _log_hls_success(hls_dir, resolution)
        return True
    logger.error(f'FFmpeg HLS error: {error}')
    return False


def _log_hls_success(hls_dir, resolution):
    """Log successful HLS conversion"""
    segment_count = len([f for f in os.listdir(hls_dir) if f.endswith('.ts')])
    logger.info(f'HLS conversion successful for {resolution}')
    logger.info(f'{segment_count} TS segments created')


def process_uploaded_video(video_id):
    """Main task for complete video processing (duration, thumbnail, HLS)"""
    video = get_video_by_id(video_id)
    if not video:
        return False
    
    logger.info(f'Start complete processing for {video.title}')
    _set_video_status(video, 'processing')
    
    get_video_duration(video_id)
    generate_thumbnail(video_id)
    _convert_all_hls_resolutions(video_id)
    
    _set_video_status(video, 'published')
    logger.info(f'Video processing completed for {video.title}')
    return True


def _set_video_status(video, status_value):
    """Update video status"""
    video.status = status_value
    video.save(update_fields=['status'])


def _convert_all_hls_resolutions(video_id):
    """Convert video to all HLS resolutions"""
    resolutions = ['360p', '480p', '720p', '1080p']
    for resolution in resolutions:
        logger.info(f'HLS conversion to {resolution}')
        convert_video_to_hls(video_id, resolution)
