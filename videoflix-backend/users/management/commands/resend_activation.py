"""Resend activation email to a user (run from videoflix-backend dir: python manage.py resend_activation <email>)."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from users.utils import generate_activation_token, send_activation_email


class Command(BaseCommand):
    help = 'Sendet den Aktivierungs-Link erneut an die angegebene E-Mail-Adresse.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='E-Mail-Adresse des Benutzers')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email'].strip()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            self.stdout.write(self.style.ERROR(f'Kein Benutzer mit E-Mail "{email}" gefunden.'))
            return
        try:
            uid, token = generate_activation_token(user)
            send_activation_email(user, uid, token)
            self.stdout.write(self.style.SUCCESS(f'Aktivierungs-E-Mail wurde an {email} gesendet.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'E-Mail konnte nicht gesendet werden: {e}'))
