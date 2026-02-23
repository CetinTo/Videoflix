"""
Clear all database data except superuser (admin) accounts.
Deletes: watch history, favorites, video ratings, comments, videos, categories, non-admin users.
Keeps: admin/superuser users, legal pages (info).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from users.models import UserWatchHistory, UserFavorite
from videos.models import VideoRating, VideoComment, Video, Category


class Command(BaseCommand):
    help = 'Clear database except admin (superuser) accounts. Keeps legal pages.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Skip confirmation prompt.',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        if not options['no_input']:
            confirm = input(
                'This will delete all users (except admin), videos, categories, '
                'comments, ratings, watch history, favorites. Continue? [y/N]: '
            )
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Aborted.'))
                return

        with transaction.atomic():
            # Order matters: remove FKs first, then referenced models
            wh_count = UserWatchHistory.objects.count()
            UserWatchHistory.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {wh_count} watch history entries.'))

            fav_count = UserFavorite.objects.count()
            UserFavorite.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {fav_count} favorites.'))

            r_count = VideoRating.objects.count()
            VideoRating.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {r_count} ratings.'))

            c_count = VideoComment.objects.count()
            VideoComment.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {c_count} comments.'))

            v_count = Video.objects.count()
            Video.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {v_count} videos.'))

            cat_count = Category.objects.count()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {cat_count} categories.'))

            non_admin = User.objects.filter(is_superuser=False)
            u_count = non_admin.count()
            non_admin.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {u_count} non-admin users.'))

        admins = User.objects.filter(is_superuser=True)
        self.stdout.write(self.style.SUCCESS(f'Done. Admin users kept: {admins.count()}'))
        for u in admins:
            self.stdout.write(f'  - {u.email} (id={u.pk})')
