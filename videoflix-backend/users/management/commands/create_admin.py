from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Creates an admin superuser if it does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        if not User.objects.filter(email='admin@videoflix.com').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@videoflix.com',
                password='adminpassword',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✓ Superuser "admin" created successfully!'))
            self.stdout.write('  Email: admin@videoflix.com')
            self.stdout.write('  Password: adminpassword')
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists.'))
