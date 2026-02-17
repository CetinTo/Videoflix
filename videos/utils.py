"""
Utility functions for video processing and file management
"""
import os
import subprocess
import logging
from django.conf import settings
from django.core.files import File
from .models import Video

logger = logging.getLogger(__name__)


def get_video_by_id(video_id):
    """Retrieve video by ID"""
    try:
        return Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        logger.error(f'Video with ID {video_id} not found')
        return None


def get_output_path(input_path, suffix):
    """Generate output file path with suffix"""
    output_dir = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_filename = f'{base_name}_{suffix}'
    return os.path.join(output_dir, output_filename)


def get_quality_settings(resolution):
    """Get video quality settings for resolution"""
    return settings.VIDEO_RESOLUTIONS.get(resolution, {})


def build_ffmpeg_command(input_path, output_path, settings_dict):
    """Build FFmpeg command for video conversion"""
    width = settings_dict.get('width', 1280)
    height = settings_dict.get('height', 720)
    bitrate = settings_dict.get('bitrate', '2800k')
    
    return [
        'ffmpeg', '-i', input_path,
        '-c:v', 'libx264', '-preset', 'medium',
        '-crf', '23', '-vf', f'scale={width}:{height}',
        '-b:v', bitrate, '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart', '-y', output_path
    ]


def build_hls_ffmpeg_command(input_path, output_dir, settings_dict):
    """Build FFmpeg command for HLS conversion"""
    width = settings_dict.get('width', 1280)
    height = settings_dict.get('height', 720)
    bitrate = settings_dict.get('bitrate', '2800k')
    m3u8_path = os.path.join(output_dir, 'index.m3u8')
    segment_pattern = os.path.join(output_dir, 'segment_%03d.ts')
    
    return [
        'ffmpeg', '-i', input_path,
        '-c:v', 'libx264', '-preset', 'medium',
        '-crf', '23', '-vf', f'scale={width}:{height}',
        '-b:v', bitrate, '-c:a', 'aac', '-b:a', '128k',
        '-f', 'hls', '-hls_time', '10',
        '-hls_list_size', '0', '-hls_segment_filename',
        segment_pattern, '-y', m3u8_path
    ]


def run_ffmpeg_command(command):
    """Execute FFmpeg command and return success status"""
    logger.info(f'Running FFmpeg: {" ".join(command)}')
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return process.returncode == 0, process.stderr


def save_video_file(video, field_name, file_path):
    """Save converted video file to model field"""
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        field = getattr(video, field_name)
        field.save(filename, File(f), save=True)


def get_video_duration_seconds(video_path):
    """Get video duration in seconds using ffprobe"""
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
        return int(duration)
    except Exception as e:
        logger.error(f'Error getting duration: {e}')
        return 0


def create_hls_directory(base_path, resolution):
    """Create HLS output directory"""
    hls_dir = os.path.join(base_path, f'hls_{resolution}')
    os.makedirs(hls_dir, exist_ok=True)
    return hls_dir


def build_thumbnail_command(input_path, output_path, timestamp='00:00:05'):
    """Build FFmpeg command for thumbnail generation"""
    return [
        'ffmpeg', '-i', input_path, '-ss', timestamp,
        '-vframes', '1', '-vf', 'scale=1280:720',
        '-q:v', '2', '-y', output_path
    ]


def save_thumbnail_file(video, file_path):
    """Save thumbnail file to video model"""
    from django.core.files import File
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        video.thumbnail.save(filename, File(f), save=True)


def update_video_duration(video, duration_seconds):
    """Update video duration field"""
    video.duration = duration_seconds
    video.save(update_fields=['duration'])
