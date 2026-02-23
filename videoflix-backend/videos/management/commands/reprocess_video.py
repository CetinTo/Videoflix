"""
Management-Befehl: Video nachträglich verarbeiten (Dauer, Thumbnail, HLS).
Nützlich wenn der RQ-Job nicht lief oder fehlgeschlagen ist.
"""
from django.core.management.base import BaseCommand
from videos.tasks import process_uploaded_video


class Command(BaseCommand):
    help = 'Video nachträglich verarbeiten (Dauer, Thumbnail, HLS)'

    def add_arguments(self, parser):
        parser.add_argument('video_id', type=int, help='ID des Videos')

    def handle(self, *args, **options):
        video_id = options['video_id']
        self.stdout.write(f'Starte Verarbeitung für Video-ID {video_id}...')
        success = process_uploaded_video(video_id)
        if success:
            self.stdout.write(self.style.SUCCESS(f'Video {video_id} erfolgreich verarbeitet.'))
        else:
            self.stdout.write(self.style.ERROR(f'Verarbeitung für Video {video_id} fehlgeschlagen. Siehe Logs.'))
