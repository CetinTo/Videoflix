"""
Utility functions for video processing, file management, and HLS streaming.

Video processing: FFmpeg commands, duration, thumbnails, HLS conversion.
File paths: get original video path, output path, etc.
HLS streaming: serve files with range support, M3U8/segment delivery.
"""
import logging
import os
import subprocess

from django.conf import settings
from django.core.files import File
from django.http import FileResponse, Http404, HttpResponse
from rest_framework import status
from rest_framework.response import Response

from .models import Video

logger = logging.getLogger(__name__)
STREAM_CHUNK_SIZE = 1024 * 1024
VALID_HLS_RESOLUTIONS = ['360p', '480p', '720p', '1080p']


def get_video_by_id(video_id):
    """Retrieve video by ID"""
    try:
        return Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        logger.error(f'Video with ID {video_id} not found')
        return None


def _try_path_from_field(video):
    """Try to get path from video.original_video.path. Returns path or None."""
    try:
        path = video.original_video.path
        if path and os.path.isfile(path):
            return path
    except Exception:
        pass
    return None


def _try_path_from_media_root(video):
    """Try path from MEDIA_ROOT + name. Returns path or None."""
    name = video.original_video.name
    if not name:
        return None
    path = os.path.join(settings.MEDIA_ROOT, name)
    return path if os.path.isfile(path) else None


def _try_fallback_path(video):
    """Fallback: videos/{id}/{filename} when DB has videos/None/ or temp_xxx/."""
    name = video.original_video.name
    if not name:
        return None
    fallback = os.path.join(settings.MEDIA_ROOT, 'videos', str(video.id), os.path.basename(name))
    return fallback if os.path.isfile(fallback) else None


def get_original_video_path(video):
    """
    Return the filesystem path of the video's original file.
    Uses MEDIA_ROOT + name if .path is not available (e.g. default storage).
    Fallback: videos/{id}/{filename} wenn DB-Pfad videos/None/ oder temp_xxx/ enthält.
    """
    if not video or not video.original_video:
        return None
    return (
        _try_path_from_field(video)
        or _try_path_from_media_root(video)
        or _try_fallback_path(video)
    )


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
    """Save thumbnail file to video model."""
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        video.thumbnail.save(filename, File(f), save=True)


def update_video_duration(video, duration_seconds):
    """Update the video's duration field (in seconds)."""
    video.duration = duration_seconds
    video.save(update_fields=['duration'])


# -----------------------------------------------------------------------------
# HLS streaming helpers (used by views.py; views only return HTTP responses)
# -----------------------------------------------------------------------------

def build_http_response(data, status_code, content_type, filename, range_info=None):
    """Build HTTP response with headers for file serving."""
    response = HttpResponse(data, status=status_code, content_type=content_type)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    response['Content-Length'] = len(data)
    if range_info:
        response['Content-Range'] = range_info
    return response


def get_byte_range_from_header(range_header, file_size, full_if_no_range):
    """Extract and validate byte range from header."""
    if not range_header or not range_header.startswith('bytes='):
        if full_if_no_range:
            return 0, file_size - 1
        return 0, min(STREAM_CHUNK_SIZE, file_size) - 1
    
    try:
        range_str = range_header[6:].strip()
        parts = range_str.split('-')
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        end = min(end, file_size - 1)
        return start, end
    except (ValueError, IndexError):
        return 0, min(STREAM_CHUNK_SIZE, file_size) - 1


def serve_file_with_range(request, file_path, content_type, filename, full_file_if_no_range=False):
    """Serve file with HTTP 206 range support or full file (200)."""
    if not os.path.exists(file_path):
        raise Http404('File not found')
    
    file_size = os.path.getsize(file_path)
    range_header = request.META.get('HTTP_RANGE', '')
    start, end = get_byte_range_from_header(range_header, file_size, full_file_if_no_range)
    length = end - start + 1
    
    with open(file_path, 'rb') as f:
        f.seek(start)
        data = f.read(length)
    
    range_info = f'bytes {start}-{end}/{file_size}'
    return build_http_response(data, 206, content_type, filename, range_info)


def get_published_video(movie_id):
    """Return the published video for the given id, or raise Http404."""
    try:
        return Video.objects.get(id=movie_id, status='published')
    except Video.DoesNotExist:
        raise Http404('Video not found')


def validate_hls_resolution(resolution):
    """Return 400 Response if resolution is invalid; otherwise None."""
    if resolution not in VALID_HLS_RESOLUTIONS:
        return Response(
            {'error': f'Invalid resolution. Valid options: {", ".join(VALID_HLS_RESOLUTIONS)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return None


def build_m3u8_path(original_path, resolution):
    """Return the path to index.m3u8 for the given resolution under the video dir."""
    video_dir = os.path.dirname(original_path)
    hls_dir = os.path.join(video_dir, f'hls_{resolution}')
    return os.path.join(hls_dir, 'index.m3u8')


def create_m3u8_response(content, filename='index.m3u8'):
    """Create M3U8 HTTP response."""
    response = HttpResponse(content, content_type='application/vnd.apple.mpegurl')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def read_m3u8_file(m3u8_path):
    """Read M3U8 file. Return None if error."""
    try:
        with open(m3u8_path, 'r') as f:
            return f.read()
    except Exception as error:
        logger.warning('Error reading M3U8: %s', error)
        return None


def build_fallback_m3u8():
    """Build fallback M3U8 playlist pointing to original.mp4."""
    return '#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:9999\n#EXTINF:9999.0,\noriginal.mp4\n#EXT-X-ENDLIST\n'


def serve_m3u8_or_fallback(m3u8_path, original_path):
    """Serve real M3U8 if exists, else fallback M3U8, else None."""
    if os.path.exists(m3u8_path):
        content = read_m3u8_file(m3u8_path)
        if content:
            return create_m3u8_response(content)
    
    if os.path.exists(original_path):
        return create_m3u8_response(build_fallback_m3u8())
    
    return None


def validate_segment_name(segment):
    r"""Raise Http404 if segment contains path traversal (.. or / or \)."""
    if '..' in segment or '/' in segment or '\\' in segment:
        raise Http404('Invalid segment name')


def serve_original_mp4(request, original_path):
    """Serve original.mp4 with range support. Raises Http404 if file missing or unreadable."""
    if not os.path.exists(original_path):
        raise Http404('Original video file not found')
    try:
        return serve_file_with_range(
            request, original_path, 'video/mp4', 'original.mp4',
            full_file_if_no_range=True
        )
    except IOError:
        raise Http404('Error reading video file')


def serve_ts_segment(original_path, resolution, segment):
    """Serve a .ts segment file. Raises Http404 if format invalid or file missing."""
    if not segment.endswith('.ts'):
        raise Http404('Invalid segment format')
    video_dir = os.path.dirname(original_path)
    hls_dir = os.path.join(video_dir, f'hls_{resolution}')
    segment_path = os.path.join(hls_dir, segment)
    if not os.path.exists(segment_path):
        raise Http404(f"Segment '{segment}' not found for {resolution}")
    try:
        response = FileResponse(
            open(segment_path, 'rb'),
            content_type='video/MP2T'
        )
        response['Content-Disposition'] = f'inline; filename="{segment}"'
        response['Accept-Ranges'] = 'bytes'
        return response
    except IOError:
        raise Http404('Error reading segment file')
