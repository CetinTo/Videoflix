"""
Populate Imprint and Privacy pages in DE and EN with operator data.
Operator: Cetin Toker, cetin.toker@web.de, Martin-Jäder-Weg 22, 87480 Weitnau
"""
from django.core.management.base import BaseCommand
from info.models import LegalPage
from info.legal_content import (
    get_imprint_de_content,
    get_imprint_en_content,
    get_privacy_de_content,
    get_privacy_en_content,
    get_terms_de_content,
    get_terms_en_content,
)


class Command(BaseCommand):
    help = 'Populate legal pages (Imprint, Privacy) in DE and EN with operator data'

    def handle(self, *args, **kwargs):
        self._create_imprint_de()
        self._create_imprint_en()
        self._create_privacy_de()
        self._create_privacy_en()
        self._create_terms_de()
        self._create_terms_en()
        self.stdout.write(self.style.SUCCESS('All legal pages (DE/EN) populated successfully!'))

    def _save_legal_page(self, page_type, language, title, content):
        """Save or update a legal page."""
        LegalPage.objects.update_or_create(
            page_type=page_type, language=language,
            defaults={'title': title, 'content': content.strip(), 'is_published': True}
        )

    def _create_imprint_de(self):
        content = get_imprint_de_content()
        self._save_legal_page('imprint', 'de', 'Impressum', content)
        self.stdout.write(self.style.SUCCESS('Imprint (DE) updated'))

    def _create_imprint_en(self):
        content = get_imprint_en_content()
        self._save_legal_page('imprint', 'en', 'Imprint', content)
        self.stdout.write(self.style.SUCCESS('Imprint (EN) updated'))

    def _create_privacy_de(self):
        content = get_privacy_de_content()
        self._save_legal_page('privacy', 'de', 'Datenschutzerklärung', content)
        self.stdout.write(self.style.SUCCESS('Privacy (DE) updated'))

    def _create_privacy_en(self):
        content = get_privacy_en_content()
        self._save_legal_page('privacy', 'en', 'Privacy Policy', content)
        self.stdout.write(self.style.SUCCESS('Privacy (EN) updated'))

    def _create_terms_de(self):
        content = get_terms_de_content()
        self._save_legal_page('terms', 'de', 'Nutzungsbedingungen', content)
        self.stdout.write(self.style.SUCCESS('Terms (DE) updated'))

    def _create_terms_en(self):
        content = get_terms_en_content()
        self._save_legal_page('terms', 'en', 'Terms of Service', content)
        self.stdout.write(self.style.SUCCESS('Terms (EN) updated'))
