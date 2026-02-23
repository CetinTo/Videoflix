"""
Prüft für ein Video, welcher Pfad in der DB steht und ob die Datei auf der Festplatte existiert.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from videos.models import Video
from videos.utils import get_original_video_path


class Command(BaseCommand):
    help = 'Prüft Video-Dateipfad (DB vs. Festplatte)'

    def add_arguments(self, parser):
        parser.add_argument('video_id', type=int, nargs='?', default=None,
                            help='Video-ID (ohne Angabe: alle Videos)')

    def handle(self, *args, **options):
        video_id = options.get('video_id')
        media_root = settings.MEDIA_ROOT
        self.stdout.write(f'MEDIA_ROOT = {media_root}')
        self.stdout.write('')

        if video_id:
            try:
                videos = [Video.objects.get(id=video_id)]
            except Video.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Video mit ID {video_id} existiert nicht.'))
                return
        else:
            videos = Video.objects.all().order_by('id')

        for video in videos:
            self.stdout.write(f'--- Video ID {video.id}: {video.title} ---')
            self.stdout.write(f'  Status: {video.status}')
            if not video.original_video:
                self.stdout.write(self.style.WARNING('  original_video: nicht gesetzt'))
                self.stdout.write('')
                continue
            name = video.original_video.name
            self.stdout.write(f'  original_video.name (DB): {name}')
            try:
                stored_path = video.original_video.path
                self.stdout.write(f'  .path: {stored_path}')
                self.stdout.write(f'  .path existiert: {os.path.isfile(stored_path)}')
            except Exception as e:
                self.stdout.write(f'  .path: (Fehler: {e})')
            full_from_name = os.path.join(media_root, name) if name else ''
            if full_from_name:
                self.stdout.write(f'  MEDIA_ROOT + name: {full_from_name}')
                self.stdout.write(f'  existiert: {os.path.isfile(full_from_name)}')
            resolved = get_original_video_path(video)
            self.stdout.write(f'  get_original_video_path(): {resolved or "(None)"}')
            if resolved:
                self.stdout.write(self.style.SUCCESS('  -> Datei wird gefunden.'))
            else:
                self.stdout.write(self.style.ERROR('  -> Datei wird NICHT gefunden (404 beim Abspielen).'))
            self.stdout.write('')
