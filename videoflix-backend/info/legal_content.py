"""
Legal page content templates (Imprint, Privacy, Terms) for populate_legal_pages.
Operator: Cetin Toker, cetin.toker@web.de, Martin-Jäder-Weg 22, 87480 Weitnau
"""
NAME = "Cetin Toker"
EMAIL = "cetin.toker@web.de"
STREET = "Martin-Jäder-Weg 22"
ZIP_CODE = "87480"
CITY = "Weitnau"
COUNTRY_DE = "Deutschland"
COUNTRY_EN = "Germany"

IMPRINT_DE = """
<h2>Impressum</h2>
<h3>Angaben gemäß § 5 TMG</h3>
<p>{name}<br>{street}<br>{zip_code} {city}<br>{country}</p>
<h3>Kontakt</h3>
<p>E-Mail: <a href="mailto:{email}">{email}</a></p>
<h3>Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h3>
<p>{name}, {street}, {zip_code} {city}</p>
<h3>EU-Streitschlichtung</h3>
<p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
<a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a><br>
Unsere E-Mail-Adresse finden Sie oben im Impressum.</p>
<h3>Verbraucherstreitbeilegung</h3>
<p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h3>Haftung für Inhalte</h3>
<p>Als Diensteanbieter sind wir gemäß § 7 Abs. 1 TMG für eigene Inhalte verantwortlich. Nach §§ 8 bis 10 TMG sind wir nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen.</p>
<h3>Haftung für Links</h3>
<p>Unser Angebot enthält Links zu externen Websites Dritter. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter verantwortlich.</p>
<h3>Urheberrecht</h3>
<p>Die Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht.</p>
<p><small>Stand: Februar 2026</small></p>
"""

IMPRINT_EN = """
<h2>Imprint / Legal Notice</h2>
<h3>Information according to § 5 TMG (Germany)</h3>
<p>{name}<br>{street}<br>{zip_code} {city}<br>{country}</p>
<h3>Contact</h3>
<p>Email: <a href="mailto:{email}">{email}</a></p>
<h3>Responsible for content (§ 55 Abs. 2 RStV)</h3>
<p>{name}, {street}, {zip_code} {city}</p>
<h3>EU dispute resolution</h3>
<p>The European Commission provides a platform for online dispute resolution (ODR): <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer">https://ec.europa.eu/consumers/odr/</a></p>
<h3>Liability for content</h3>
<p>As a service provider we are responsible for our own content on these pages. We are not obliged to monitor third-party information.</p>
<h3>Liability for links</h3>
<p>Our site contains links to external websites. We have no influence on their content.</p>
<h3>Copyright</h3>
<p>Content on these pages is subject to German copyright law.</p>
<p><small>Last updated: February 2026</small></p>
"""

PRIVACY_DE = """
<h2>Datenschutzerklärung</h2>
<h3>1. Datenschutz auf einen Blick</h3>
<p>Personenbezogene Daten sind alle Daten, mit denen Sie persönlich identifiziert werden können.</p>
<h3>2. Verantwortliche Stelle</h3>
<p>{name}<br>{street}<br>{zip_code} {city}<br>{country}<br>E-Mail: <a href="mailto:{email}">{email}</a></p>
<h3>3. Datenerfassung auf dieser Website</h3>
<p>Ihre Daten werden erhoben, wenn Sie uns diese mitteilen (z. B. Registrierung, Kontaktformular) oder automatisch beim Besuch (technische Daten, Logs).</p>
<h3>4. Cookies und Server-Logdateien</h3>
<p>Wir setzen Session-Cookies ein. Der Provider speichert u. a. Browsertyp, Referrer-URL, Hostname und Uhrzeit der Anfrage.</p>
<h3>5. Registrierung und Konto</h3>
<p>Die bei der Registrierung eingegebenen Daten verwenden wir nur für den jeweiligen Dienst (Videoflix).</p>
<h3>6. Ihre Rechte</h3>
<p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Widerspruch und Datenübertragbarkeit.</p>
<p><small>Stand: Februar 2026</small></p>
"""

PRIVACY_EN = """
<h2>Privacy Policy</h2>
<h3>1. Overview</h3>
<p>Personal data means any data by which you can be personally identified.</p>
<h3>2. Data controller</h3>
<p>{name}<br>{street}<br>{zip_code} {city}<br>{country}<br>Email: <a href="mailto:{email}">{email}</a></p>
<h3>3. Data collection on this website</h3>
<p>We collect data when you provide it (e.g. registration, contact form) or automatically when you visit (technical data, server logs).</p>
<h3>4. Cookies and server logs</h3>
<p>We use session cookies. The provider stores browser type, referrer URL, hostname and time of request.</p>
<h3>5. Registration and account</h3>
<p>Data entered during registration is used only for the Videoflix service.</p>
<h3>6. Your rights</h3>
<p>You have the right to access, rectification, erasure, restriction of processing, objection and data portability.</p>
<p><small>Last updated: February 2026</small></p>
"""

TERMS_DE = """
<h2>Nutzungsbedingungen</h2>
<h3>1. Geltungsbereich</h3>
<p>Diese Bedingungen gelten für die Nutzung der Videoflix-Plattform.</p>
<h3>2. Vertragsschluss</h3>
<p>Der Vertrag kommt durch Registrierung und E-Mail-Bestätigung zustande.</p>
<h3>3. Nutzerkonto</h3>
<p>Wahrheitsgemäße Angaben, vertrauliche Zugangsdaten, Verantwortung für Aktivitäten unter Ihrem Konto.</p>
<h3>4. Verboten</h3>
<p>Weitergabe von Zugangsdaten, technische Manipulation, Verletzung von Urheberrechten.</p>
<h3>5. Datenschutz</h3>
<p>Verarbeitung gemäß unserer Datenschutzerklärung.</p>
<p><small>Stand: Februar 2026</small></p>
"""

TERMS_EN = """
<h2>Terms of Service</h2>
<h3>1. Scope</h3>
<p>These terms apply to the use of the Videoflix platform.</p>
<h3>2. Contract</h3>
<p>The contract is formed by registration and email confirmation.</p>
<h3>3. User account</h3>
<p>Accurate information, confidential credentials, responsibility for activities under your account.</p>
<h3>4. Prohibited</h3>
<p>Sharing credentials, technical manipulation, infringement of copyrights.</p>
<h3>5. Privacy</h3>
<p>Processing in accordance with our Privacy Policy.</p>
<p><small>Last updated: February 2026</small></p>
"""


def _op_data(country):
    """Return operator data dict for template formatting."""
    return {
        'name': NAME, 'email': EMAIL, 'street': STREET,
        'zip_code': ZIP_CODE, 'city': CITY, 'country': country,
    }


def get_imprint_de_content():
    """Return German imprint HTML content."""
    return IMPRINT_DE.format(**_op_data(COUNTRY_DE))


def get_imprint_en_content():
    """Return English imprint HTML content."""
    return IMPRINT_EN.format(**_op_data(COUNTRY_EN))


def get_privacy_de_content():
    """Return German privacy policy HTML content."""
    return PRIVACY_DE.format(**_op_data(COUNTRY_DE))


def get_privacy_en_content():
    """Return English privacy policy HTML content."""
    return PRIVACY_EN.format(**_op_data(COUNTRY_EN))


def get_terms_de_content():
    """Return German terms of service HTML content."""
    return TERMS_DE


def get_terms_en_content():
    """Return English terms of service HTML content."""
    return TERMS_EN
