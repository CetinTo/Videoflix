"""
Video Processing Tasks mit Django-RQ
Verwendet ffmpeg zur Video-Konvertierung in verschiedene Qualitäten
"""
import os
import subprocess
import logging
from django.conf import settings
from django.core.files import File
from .models import Video

logger = logging.getLogger(__name__)


def convert_video_to_quality(video_id, resolution='720p'):
    """
    Konvertiert ein Video in eine bestimmte Qualität
    
    Args:
        video_id: ID des Video-Objekts
        resolution: Ziel-Auflösung (360p, 480p, 720p, 1080p)
    """
    try:
        video = Video.objects.get(id=video_id)
        logger.info(f'Starte Konvertierung für Video {video.title} zu {resolution}')
        
        # Original Video Pfad
        input_path = video.original_video.path
        
        # Output Pfad generieren
        output_dir = os.path.dirname(input_path)
        filename_without_ext = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f'{filename_without_ext}_{resolution}.mp4'
        output_path = os.path.join(output_dir, output_filename)
        
        # Video-Einstellungen basierend auf Auflösung
        quality_settings = settings.VIDEO_RESOLUTIONS.get(resolution, {})
        width = quality_settings.get('width', 1280)
        height = quality_settings.get('height', 720)
        bitrate = quality_settings.get('bitrate', '2800k')
        
        # ffmpeg Befehl
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',  # H.264 Codec
            '-preset', 'medium',  # Encoding-Geschwindigkeit
            '-crf', '23',  # Quality (18-28, niedriger = besser)
            '-vf', f'scale={width}:{height}',  # Skalierung
            '-b:v', bitrate,  # Video Bitrate
            '-c:a', 'aac',  # Audio Codec
            '-b:a', '128k',  # Audio Bitrate
            '-movflags', '+faststart',  # Für Web-Streaming
            '-y',  # Überschreibe Output-Datei
            output_path
        ]
        
        logger.info(f'Führe ffmpeg aus: {" ".join(ffmpeg_command)}')
        
        # ffmpeg ausführen
        process = subprocess.run(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode == 0:
            logger.info(f'Konvertierung erfolgreich: {output_path}')
            
            # Speichere konvertiertes Video im Model
            with open(output_path, 'rb') as f:
                field_name = f'video_{resolution}'
                field = getattr(video, field_name)
                field.save(output_filename, File(f), save=True)
            
            logger.info(f'Video {resolution} gespeichert für {video.title}')
            return True
        else:
            logger.error(f'ffmpeg Fehler: {process.stderr}')
            return False
            
    except Video.DoesNotExist:
        logger.error(f'Video mit ID {video_id} nicht gefunden')
        return False
    except Exception as e:
        logger.error(f'Fehler bei Video-Konvertierung: {str(e)}')
        return False


def generate_thumbnail(video_id, timestamp='00:00:05'):
    """
    Generiert ein Thumbnail aus einem Video
    
    Args:
        video_id: ID des Video-Objekts
        timestamp: Zeitpunkt im Video (Format: HH:MM:SS)
    """
    try:
        video = Video.objects.get(id=video_id)
        logger.info(f'Generiere Thumbnail für Video {video.title}')
        
        # Input Video Pfad
        input_path = video.original_video.path
        
        # Output Pfad generieren
        output_dir = os.path.dirname(input_path)
        filename_without_ext = os.path.splitext(os.path.basename(input_path))[0]
        thumbnail_filename = f'{filename_without_ext}_thumbnail.jpg'
        thumbnail_path = os.path.join(output_dir, thumbnail_filename)
        
        # ffmpeg Befehl für Thumbnail
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,
            '-ss', timestamp,  # Zeitpunkt
            '-vframes', '1',  # Ein Frame
            '-vf', 'scale=1280:720',  # Skalierung
            '-q:v', '2',  # Qualität (2-31, niedriger = besser)
            '-y',
            thumbnail_path
        ]
        
        logger.info(f'Führe ffmpeg aus: {" ".join(ffmpeg_command)}')
        
        # ffmpeg ausführen
        process = subprocess.run(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode == 0:
            logger.info(f'Thumbnail erfolgreich generiert: {thumbnail_path}')
            
            # Speichere Thumbnail im Model
            with open(thumbnail_path, 'rb') as f:
                video.thumbnail.save(thumbnail_filename, File(f), save=True)
            
            logger.info(f'Thumbnail gespeichert für {video.title}')
            return True
        else:
            logger.error(f'ffmpeg Fehler: {process.stderr}')
            return False
            
    except Video.DoesNotExist:
        logger.error(f'Video mit ID {video_id} nicht gefunden')
        return False
    except Exception as e:
        logger.error(f'Fehler bei Thumbnail-Generierung: {str(e)}')
        return False


def get_video_duration(video_id):
    """
    Ermittelt die Dauer eines Videos mit ffprobe
    
    Args:
        video_id: ID des Video-Objekts
    """
    try:
        video = Video.objects.get(id=video_id)
        logger.info(f'Ermittle Dauer für Video {video.title}')
        
        input_path = video.original_video.path
        
        # ffprobe Befehl
        ffprobe_command = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]
        
        # ffprobe ausführen
        process = subprocess.run(
            ffprobe_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if process.returncode == 0:
            duration = float(process.stdout.strip())
            video.duration = int(duration)
            video.save(update_fields=['duration'])
            logger.info(f'Dauer gespeichert: {video.duration} Sekunden')
            return True
        else:
            logger.error(f'ffprobe Fehler: {process.stderr}')
            return False
            
    except Video.DoesNotExist:
        logger.error(f'Video mit ID {video_id} nicht gefunden')
        return False
    except Exception as e:
        logger.error(f'Fehler bei Dauer-Ermittlung: {str(e)}')
        return False


def convert_video_to_hls(video_id, resolution='720p'):
    """
    Konvertiert ein Video zu HLS (HTTP Live Streaming) Format
    Erstellt M3U8 Playlist und TS Segmente
    
    Args:
        video_id: ID des Video-Objekts
        resolution: Ziel-Auflösung (360p, 480p, 720p, 1080p)
    """
    try:
        video = Video.objects.get(id=video_id)
        logger.info(f'Starte HLS-Konvertierung für Video {video.title} zu {resolution}')
        
        # Original Video Pfad
        input_path = video.original_video.path
        
        # Output Verzeichnis für HLS-Dateien
        output_dir = os.path.dirname(input_path)
        filename_without_ext = os.path.splitext(os.path.basename(input_path))[0]
        
        # HLS-spezifischer Ordner für diese Auflösung
        hls_dir = os.path.join(output_dir, f'hls_{resolution}')
        os.makedirs(hls_dir, exist_ok=True)
        
        # M3U8 und TS Dateipfade
        m3u8_filename = 'index.m3u8'
        m3u8_path = os.path.join(hls_dir, m3u8_filename)
        segment_pattern = os.path.join(hls_dir, 'segment_%03d.ts')
        
        # Video-Einstellungen basierend auf Auflösung
        quality_settings = settings.VIDEO_RESOLUTIONS.get(resolution, {})
        width = quality_settings.get('width', 1280)
        height = quality_settings.get('height', 720)
        bitrate = quality_settings.get('bitrate', '2800k')
        
        # FFmpeg Befehl für HLS
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',  # H.264 Video Codec
            '-c:a', 'aac',  # AAC Audio Codec
            '-preset', 'medium',
            '-crf', '23',
            '-vf', f'scale={width}:{height}',
            '-b:v', bitrate,
            '-b:a', '128k',  # Audio Bitrate
            '-hls_time', '10',  # Segment-Länge: 10 Sekunden
            '-hls_list_size', '0',  # Alle Segmente in Playlist
            '-hls_segment_filename', segment_pattern,
            '-start_number', '0',
            '-f', 'hls',
            '-y',  # Überschreibe existierende Dateien
            m3u8_path
        ]
        
        logger.info(f'Führe FFmpeg HLS aus: {" ".join(ffmpeg_command)}')
        
        # FFmpeg ausführen
        process = subprocess.run(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3600  # 1 Stunde Timeout
        )
        
        if process.returncode == 0:
            logger.info(f'HLS-Konvertierung erfolgreich für {resolution}')
            logger.info(f'M3U8 Playlist: {m3u8_path}')
            
            # Zähle generierte Segmente
            segment_count = len([f for f in os.listdir(hls_dir) if f.endswith('.ts')])
            logger.info(f'{segment_count} TS-Segmente erstellt')
            
            return True
        else:
            logger.error(f'FFmpeg Fehler (HLS): {process.stderr}')
            return False
            
    except Video.DoesNotExist:
        logger.error(f'Video mit ID {video_id} nicht gefunden')
        return False
    except Exception as e:
        logger.error(f'Fehler bei HLS-Konvertierung: {str(e)}')
        return False


def process_uploaded_video(video_id):
    """
    Haupt-Task zur vollständigen Verarbeitung eines hochgeladenen Videos
    
    - Ermittelt Dauer
    - Generiert Thumbnail
    - Konvertiert zu HLS in verschiedenen Qualitäten
    
    Args:
        video_id: ID des Video-Objekts
    """
    try:
        video = Video.objects.get(id=video_id)
        logger.info(f'Starte vollständige Verarbeitung für Video {video.title}')
        
        # Status auf "processing" setzen
        video.status = 'processing'
        video.save(update_fields=['status'])
        
        # 1. Dauer ermitteln
        logger.info('Schritt 1: Dauer ermitteln')
        get_video_duration(video_id)
        
        # 2. Thumbnail generieren
        logger.info('Schritt 2: Thumbnail generieren')
        generate_thumbnail(video_id)
        
        # 3. Videos zu HLS in verschiedenen Qualitäten konvertieren
        resolutions = ['360p', '480p', '720p', '1080p']
        for resolution in resolutions:
            logger.info(f'Schritt 3: HLS-Konvertierung zu {resolution}')
            convert_video_to_hls(video_id, resolution)
        
        # Status auf "published" setzen
        video.status = 'published'
        video.save(update_fields=['status'])
        
        logger.info(f'Video-Verarbeitung abgeschlossen für {video.title}')
        return True
        
    except Video.DoesNotExist:
        logger.error(f'Video mit ID {video_id} nicht gefunden')
        return False
    except Exception as e:
        logger.error(f'Fehler bei Video-Verarbeitung: {str(e)}')
        # Status auf "draft" zurücksetzen bei Fehler
        try:
            video = Video.objects.get(id=video_id)
            video.status = 'draft'
            video.save(update_fields=['status'])
        except:
            pass
        return False
