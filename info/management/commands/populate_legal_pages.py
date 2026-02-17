from django.core.management.base import BaseCommand
from info.models import LegalPage


class Command(BaseCommand):
    help = 'Populate legal pages with default content'

    def handle(self, *args, **kwargs):
        # Privacy Policy
        privacy_content = """
        <h2>Datenschutzerklärung</h2>
        
        <h3>1. Datenschutz auf einen Blick</h3>
        <h4>Allgemeine Hinweise</h4>
        <p>Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten 
        passiert, wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit denen Sie persönlich 
        identifiziert werden können.</p>
        
        <h4>Datenerfassung auf dieser Website</h4>
        <p><strong>Wer ist verantwortlich für die Datenerfassung auf dieser Website?</strong></p>
        <p>Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber. Dessen Kontaktdaten können 
        Sie dem Impressum dieser Website entnehmen.</p>
        
        <p><strong>Wie erfassen wir Ihre Daten?</strong></p>
        <p>Ihre Daten werden zum einen dadurch erhoben, dass Sie uns diese mitteilen. Hierbei kann es sich z.B. um 
        Daten handeln, die Sie in ein Kontaktformular eingeben.</p>
        <p>Andere Daten werden automatisch oder nach Ihrer Einwilligung beim Besuch der Website durch unsere 
        IT-Systeme erfasst. Das sind vor allem technische Daten (z.B. Internetbrowser, Betriebssystem oder Uhrzeit 
        des Seitenaufrufs).</p>
        
        <p><strong>Wofür nutzen wir Ihre Daten?</strong></p>
        <p>Ein Teil der Daten wird erhoben, um eine fehlerfreie Bereitstellung der Website zu gewährleisten. 
        Andere Daten können zur Analyse Ihres Nutzerverhaltens verwendet werden.</p>
        
        <h3>2. Hosting</h3>
        <p>Wir hosten die Inhalte unserer Website bei folgendem Anbieter:</p>
        <p>Externer Hoster: Diese Website wird extern gehostet. Die personenbezogenen Daten, die auf dieser 
        Website erfasst werden, werden auf den Servern des Hosters / der Hoster gespeichert.</p>
        
        <h3>3. Allgemeine Hinweise und Pflichtinformationen</h3>
        <h4>Datenschutz</h4>
        <p>Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre 
        personenbezogenen Daten vertraulich und entsprechend den gesetzlichen Datenschutzvorschriften sowie 
        dieser Datenschutzerklärung.</p>
        
        <h4>Hinweis zur verantwortlichen Stelle</h4>
        <p>Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:</p>
        <p>
        Cetin Toker<br>
        Martin-Jäger-Weg 22<br>
        87480 Weitnau<br>
        Deutschland
        </p>
        <p>
        E-Mail: cetin.toker@web.de
        </p>
        
        <h4>Speicherdauer</h4>
        <p>Soweit innerhalb dieser Datenschutzerklärung keine speziellere Speicherdauer genannt wurde, verbleiben 
        Ihre personenbezogenen Daten bei uns, bis der Zweck für die Datenverarbeitung entfällt.</p>
        
        <h3>4. Datenerfassung auf dieser Website</h3>
        <h4>Cookies</h4>
        <p>Unsere Internetseiten verwenden so genannte „Cookies". Cookies sind kleine Datenpakete und richten auf 
        Ihrem Endgerät keinen Schaden an. Sie werden entweder vorübergehend für die Dauer einer Sitzung 
        (Session-Cookies) oder dauerhaft (permanente Cookies) auf Ihrem Endgerät gespeichert.</p>
        
        <h4>Server-Log-Dateien</h4>
        <p>Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten Server-Log-Dateien, 
        die Ihr Browser automatisch an uns übermittelt. Dies sind:</p>
        <ul>
            <li>Browsertyp und Browserversion</li>
            <li>verwendetes Betriebssystem</li>
            <li>Referrer URL</li>
            <li>Hostname des zugreifenden Rechners</li>
            <li>Uhrzeit der Serveranfrage</li>
            <li>IP-Adresse</li>
        </ul>
        
        <h4>Registrierung auf dieser Website</h4>
        <p>Sie können sich auf dieser Website registrieren, um zusätzliche Funktionen auf der Seite zu nutzen. 
        Die dazu eingegebenen Daten verwenden wir nur zum Zwecke der Nutzung des jeweiligen Angebotes oder 
        Dienstes, für den Sie sich registriert haben.</p>
        
        <h3>5. Ihre Rechte</h3>
        <p>Sie haben jederzeit das Recht:</p>
        <ul>
            <li>Auskunft über Ihre bei uns gespeicherten personenbezogenen Daten zu erhalten</li>
            <li>die Berichtigung unrichtiger personenbezogener Daten zu verlangen</li>
            <li>die Löschung Ihrer bei uns gespeicherten personenbezogenen Daten zu verlangen</li>
            <li>die Einschränkung der Datenverarbeitung zu verlangen</li>
            <li>Widerspruch gegen die Verarbeitung Ihrer Daten einzulegen</li>
            <li>Datenübertragbarkeit zu verlangen</li>
        </ul>
        
        <p>Stand: Februar 2026</p>
        """
        
        privacy_page, created = LegalPage.objects.update_or_create(
            page_type='privacy',
            defaults={
                'title': 'Datenschutzerklärung',
                'content': privacy_content,
                'is_published': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Privacy policy created'))
        else:
            self.stdout.write(self.style.SUCCESS('Privacy policy updated'))
        
        # Imprint
        imprint_content = """
        <h2>Impressum</h2>
        
        <h3>Angaben gemäß § 5 TMG</h3>
        <p>
        Cetin Toker<br>
        Martin-Jäger-Weg 22<br>
        87480 Weitnau<br>
        Deutschland
        </p>
        
        <h3>Kontakt</h3>
        <p>
        E-Mail: cetin.toker@web.de
        </p>
        
        <h3>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h3>
        <p>
        Cetin Toker<br>
        Martin-Jäger-Weg 22<br>
        87480 Weitnau
        </p>
        
        <h3>EU-Streitschlichtung</h3>
        <p>
        Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: 
        <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">
        https://ec.europa.eu/consumers/odr/</a><br>
        Unsere E-Mail-Adresse finden Sie oben im Impressum.
        </p>
        
        <h3>Verbraucherstreitbeilegung/Universalschlichtungsstelle</h3>
        <p>
        Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer 
        Verbraucherschlichtungsstelle teilzunehmen.
        </p>
        
        <h3>Haftung für Inhalte</h3>
        <p>
        Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den 
        allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht 
        verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen 
        zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
        </p>
        
        <h3>Haftung für Links</h3>
        <p>
        Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. 
        Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der 
        verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.
        </p>
        
        <h3>Urheberrecht</h3>
        <p>
        Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen 
        Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der 
        Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.
        </p>
        
        <p>Stand: Februar 2026</p>
        """
        
        imprint_page, created = LegalPage.objects.update_or_create(
            page_type='imprint',
            defaults={
                'title': 'Impressum',
                'content': imprint_content,
                'is_published': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Imprint created'))
        else:
            self.stdout.write(self.style.SUCCESS('Imprint updated'))
        
        # Terms of Service
        terms_content = """
        <h2>Nutzungsbedingungen</h2>
        
        <h3>1. Geltungsbereich</h3>
        <p>Diese Nutzungsbedingungen gelten für die Nutzung der Videoflix-Plattform. Mit der Registrierung 
        und Nutzung unserer Dienste erklären Sie sich mit diesen Bedingungen einverstanden.</p>
        
        <h3>2. Vertragsschluss</h3>
        <p>Der Vertrag über die Nutzung der Videoflix-Dienste kommt durch Ihre Registrierung und die 
        Bestätigung Ihrer E-Mail-Adresse zustande.</p>
        
        <h3>3. Leistungsumfang</h3>
        <p>Videoflix bietet einen Video-Streaming-Dienst, der es registrierten Nutzern ermöglicht, 
        Videos in verschiedenen Qualitätsstufen (360p, 480p, 720p, 1080p) anzusehen.</p>
        
        <h3>4. Nutzerkonto</h3>
        <ul>
            <li>Sie sind verpflichtet, bei der Registrierung wahrheitsgemäße Angaben zu machen</li>
            <li>Ihre Zugangsdaten sind vertraulich zu behandeln und vor Zugriff Dritter zu schützen</li>
            <li>Sie sind für alle Aktivitäten unter Ihrem Konto verantwortlich</li>
            <li>Bei Verdacht auf unbefugten Zugriff müssen Sie uns umgehend informieren</li>
        </ul>
        
        <h3>5. Verbotene Nutzung</h3>
        <p>Folgende Handlungen sind untersagt:</p>
        <ul>
            <li>Weitergabe Ihrer Zugangsdaten an Dritte</li>
            <li>Technische Manipulation oder Umgehung von Schutzmechanismen</li>
            <li>Automatisiertes Auslesen von Inhalten (Screen Scraping)</li>
            <li>Upload von schädlicher Software oder Viren</li>
            <li>Verletzung von Urheberrechten oder anderen Rechten Dritter</li>
        </ul>
        
        <h3>6. Verfügbarkeit</h3>
        <p>Wir bemühen uns um eine hohe Verfügbarkeit unserer Dienste. Es besteht jedoch kein Anspruch auf 
        eine ununterbrochene oder fehlerfreie Verfügbarkeit.</p>
        
        <h3>7. Haftung</h3>
        <p>Wir haften für Vorsatz und grobe Fahrlässigkeit. Bei einfacher Fahrlässigkeit haften wir nur bei 
        Verletzung wesentlicher Vertragspflichten.</p>
        
        <h3>8. Datenschutz</h3>
        <p>Die Verarbeitung Ihrer personenbezogenen Daten erfolgt gemäß unserer Datenschutzerklärung.</p>
        
        <h3>9. Kündigung</h3>
        <p>Sie können Ihr Konto jederzeit löschen. Wir behalten uns das Recht vor, Konten bei Verstößen 
        gegen diese Nutzungsbedingungen zu sperren oder zu löschen.</p>
        
        <h3>10. Änderungen der Nutzungsbedingungen</h3>
        <p>Wir behalten uns vor, diese Nutzungsbedingungen zu ändern. Sie werden über Änderungen per 
        E-Mail informiert.</p>
        
        <h3>11. Schlussbestimmungen</h3>
        <p>Es gilt das Recht der Bundesrepublik Deutschland. Gerichtsstand ist Musterstadt.</p>
        
        <p>Stand: Februar 2026</p>
        """
        
        terms_page, created = LegalPage.objects.update_or_create(
            page_type='terms',
            defaults={
                'title': 'Nutzungsbedingungen',
                'content': terms_content,
                'is_published': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Terms of service created'))
        else:
            self.stdout.write(self.style.SUCCESS('Terms of service updated'))
        
        self.stdout.write(self.style.SUCCESS('All legal pages populated successfully!'))
