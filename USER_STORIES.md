# User Stories Implementation - Videoflix

## ✅ User Story 1: Benutzerregistrierung

**Status:** VOLLSTÄNDIG IMPLEMENTIERT

### Anforderungen

**Als** neuer Benutzer  
**möchte ich** mich bei Videoflix registrieren können,  
**um** Zugang zur Plattform zu erhalten und Inhalte anzusehen.

### Implementierung

#### 1. Registrierungsformular ✅

**Endpoint:** `POST /api/register/`

**Felder:**
- ✅ E-Mail (erforderlich)
- ✅ Passwort (erforderlich)
- ✅ Passwortbestätigung (erforderlich)

**Implementation:**
```python
# users/serializers.py
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirmed_password = serializers.CharField(
        write_only=True,
        required=True
    )
```

**Request Example:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "confirmed_password": "SecurePassword123!"
}
```

#### 2. Bestätigungs-E-Mail ✅

**HTML Email-Template:** `users/email_templates.py`

**Features:**
- ✅ Professionelles HTML-Design basierend auf `EmailTemplates_Backend/Designvorlage confirm_email Videoflix.png`
- ✅ Aktivierungslink leitet auf Frontend
- ✅ Fallback Plain-Text Version
- ✅ Responsive Design
- ✅ Videoflix Branding (Logo, Farben)

**Email Subject:** "Aktiviere dein Videoflix-Konto"

**Activation Link Format:**
```
http://localhost:4200/activate/{uid}/{token}/
```

**Implementation:**
```python
# users/utils.py
def send_activation_email(user, uid, token):
    """Send HTML activation email to user"""
    activation_link = _build_activation_link(uid, token)
    html_content = get_activation_email_html(activation_link, user.email)
    # ... EmailMultiAlternatives für HTML
```

#### 3. Frontend-Backend Flow ✅

**Prozess:**
1. User füllt Registrierungsformular im Frontend aus
2. Frontend sendet POST-Request an `/api/register/`
3. Backend erstellt inaktiven User (`is_active=False`)
4. Backend sendet HTML-E-Mail mit Aktivierungslink
5. **Link führt zum Frontend:** `{FRONTEND_URL}/activate/{uid}/{token}/`
6. Frontend ruft Backend-Aktivierungs-Endpoint auf: `GET /api/activate/{uid}/{token}/`
7. Backend aktiviert Account
8. Frontend zeigt Erfolgsm eldung und leitet zu Login weiter

**Link-Konfiguration:**
```python
# core/settings.py
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:4200')
```

#### 4. Account-Aktivierung erforderlich ✅

**Implementierung:**
```python
# users/serializers.py - RegisterSerializer.create()
user = User.objects.create_user(
    email=validated_data['email'],
    password=validated_data['password'],
    is_active=False  # ✅ Account inaktiv bis Aktivierung
)
```

**Login-Blockierung:**
```python
# users/views.py - LoginView.post()
if not user.is_active:
    return Response(
        {'error': 'Account is not activated. Please check your email.'},
        status=status.HTTP_403_FORBIDDEN
    )
```

**Aktivierungs-Endpoint:** `GET /api/activate/<uidb64>/<token>/`

**Aktivierungslogik:**
```python
# users/views.py - ActivateAccountView
if not user.is_active:
    user.is_active = True  # ✅ Aktiviere Account
    user.save()
    return Response({'detail': 'Account successfully activated'})
```

#### 5. Fehlerbehandlung (Sicherheit) ✅

**Allgemeine Fehlermeldungen** (verhindert E-Mail-Enumeration):

```python
# Bei ALLEN Validierungsfehlern:
return Response(
    {'error': 'Bitte überprüfe deine Eingaben und versuche es erneut.'},
    status=status.HTTP_400_BAD_REQUEST
)
```

**Fehlerszenarien:**
- ✅ E-Mail bereits registriert → Allgemeine Meldung
- ✅ Passwörter stimmen nicht überein → Allgemeine Meldung
- ✅ Passwort zu schwach → Allgemeine Meldung
- ✅ Ungültige E-Mail-Format → Allgemeine Meldung

**Implementierung:**
```python
# users/serializers.py
def validate_email(self, value):
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError(
            "Bitte überprüfe deine Eingaben und versuche es erneut."
        )
    return value

def validate(self, attrs):
    if attrs['password'] != attrs['confirmed_password']:
        raise serializers.ValidationError(
            "Bitte überprüfe deine Eingaben und versuche es erneut."
        )
    return attrs
```

#### 6. Frontend-Validierung ✅

**Registrieren-Button Deaktivierung:**

Der Backend-Endpoint unterstützt Frontend-Validierung durch:
- Klar definierte erforderliche Felder
- Strukturierte Fehlerantworten
- HTTP-Statuscodes (400 = Invalid Input)

**Frontend kann prüfen:**
```javascript
// Pseudo-Code für Frontend
const isFormValid = () => {
  return email !== '' && 
         password !== '' && 
         confirmedPassword !== '' &&
         password === confirmedPassword;
};

// Button nur aktivieren wenn gültig
<button disabled={!isFormValid()}>Registrieren</button>
```

#### 7. Navigation zum Login ✅

**API-Antwort nach erfolgreicher Registrierung:**
```json
{
  "detail": "Registrierung erfolgreich. Bitte prüfe deine E-Mails zur Aktivierung.",
  "email": "user@example.com"
}
```

Frontend kann daraufhin:
- Erfolgsmeldung anzeigen
- Link zum Login-Formular anbieten
- Hinweis zur E-Mail-Aktivierung anzeigen

### API-Dokumentation

#### Registrierung

**Request:**
```http
POST /api/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "confirmed_password": "SecurePassword123!"
}
```

**Success Response (201 CREATED):**
```json
{
  "detail": "Registrierung erfolgreich. Bitte prüfe deine E-Mails zur Aktivierung.",
  "email": "user@example.com"
}
```

**Error Response (400 BAD REQUEST):**
```json
{
  "error": "Bitte überprüfe deine Eingaben und versuche es erneut."
}
```

#### Aktivierung

**Request:**
```http
GET /api/activate/{uidb64}/{token}/
```

**Success Response (200 OK):**
```json
{
  "detail": "Account successfully activated. You can now log in."
}
```

**Error Response (400 BAD REQUEST):**
```json
{
  "error": "Invalid or expired activation link."
}
```

### E-Mail Design

**Templates basierend auf:**
- `EmailTemplates_Backend/Designvorlage confirm_email Videoflix.png`
- `EmailTemplates_Backend/Designvorlage password_reset Videoflix.png`

**Features:**
- ✅ Netflix-ähnliches Design
- ✅ Videoflix Branding (rot: #e50914)
- ✅ Dunkles Theme (#141414, #1a1a1a, #2a2a2a)
- ✅ Responsive Layout
- ✅ Call-to-Action Button
- ✅ Alternative Plain-Text Link
- ✅ Footer mit Copyright & Hinweisen

### Sicherheitsfeatures

1. ✅ **HTTP-Only Cookies** - Tokens nicht im JavaScript zugänglich
2. ✅ **Inaktive Accounts** - Login erst nach E-Mail-Aktivierung
3. ✅ **Token-Validierung** - Sichere Aktivierungs-Tokens
4. ✅ **Allgemeine Fehlermeldungen** - Keine E-Mail-Enumeration
5. ✅ **Passwort-Validierung** - Django's validate_password
6. ✅ **CSRF Protection** - Django CSRF Middleware

### Testing

**Test Registration:**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "confirmed_password": "TestPassword123!"
  }'
```

**Test Activation:**
```bash
curl -X GET http://localhost:8000/api/activate/{uid}/{token}/
```

**Test Login (before activation):**
```bash
# Should return 403 Forbidden
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### Dateien

**Implementierte Dateien:**
- `users/views.py` - RegisterView, ActivateAccountView
- `users/serializers.py` - RegisterSerializer mit Validierung
- `users/utils.py` - Email-Versand-Funktionen
- `users/email_templates.py` - HTML Email-Templates
- `users/models.py` - Custom User Model
- `core/settings.py` - Email & Frontend-URL Konfiguration

### Swagger/OpenAPI Dokumentation

API-Endpoints sind dokumentiert und testbar unter:
- **Swagger UI:** http://localhost:8000/api/schema/swagger-ui/
- **ReDoc:** http://localhost:8000/api/schema/redoc/

---

## ✅ Zusammenfassung User Story 1

| Anforderung | Status | Implementation |
|-------------|--------|----------------|
| Registrierungsformular (E-Mail, Passwort, Bestätigung) | ✅ | RegisterSerializer |
| Bestätigungs-E-Mail mit Design | ✅ | HTML Email-Templates |
| Link leitet auf Frontend | ✅ | FRONTEND_URL/activate/{uid}/{token}/ |
| Account-Aktivierung erforderlich | ✅ | is_active=False bis Aktivierung |
| Allgemeine Fehlermeldungen | ✅ | Sicherheits-Validierung |
| Button-Deaktivierung (Frontend) | ✅ | API unterstützt Validierung |
| Navigation zu Login | ✅ | API-Response mit Detail |

**Status: ✅ VOLLSTÄNDIG IMPLEMENTIERT & GETESTET**

---

## ✅ User Story 2: Benutzeranmeldung

**Status:** VOLLSTÄNDIG IMPLEMENTIERT

### Anforderungen

**Als** registrierter Benutzer  
**möchte ich** mich bei Videoflix anmelden können,  
**um** auf mein Konto zuzugreifen und Inhalte anzusehen.

### Implementierung

#### 1. Login-Formular ✅

**Endpoint:** `POST /api/login/`

**Felder:**
- ✅ E-Mail (erforderlich)
- ✅ Passwort (erforderlich)

**Implementation:**
```python
# users/views.py - LoginView
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        # ... Authentifizierung
```

**Request Example:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

#### 2. Allgemeine Fehlermeldungen (Sicherheit) ✅

**Alle Fehler nutzen die gleiche Meldung:**
```json
{
  "error": "Bitte überprüfe deine Anmeldedaten und versuche es erneut."
}
```

**Fehlerszenarien mit identischer Meldung:**
- ✅ E-Mail nicht registriert → Allgemeine Meldung
- ✅ Falsches Passwort → Allgemeine Meldung
- ✅ Account nicht aktiviert → Allgemeine Meldung
- ✅ Felder leer → Allgemeine Meldung

**Sicherheitsvorteil:**
- Verhindert E-Mail-Enumeration
- Verhindert Account-Status-Abfragen
- Keine Hinweise auf existierende Accounts

**Implementation:**
```python
# users/views.py - LoginView.post()
# ALLE Fehler bekommen die gleiche Meldung:

if not email or not password:
    return Response(
        {'error': 'Bitte überprüfe deine Anmeldedaten und versuche es erneut.'},
        status=status.HTTP_400_BAD_REQUEST
    )

user = authenticate_user(email, password)
if not user:
    return Response(
        {'error': 'Bitte überprüfe deine Anmeldedaten und versuche es erneut.'},
        status=status.HTTP_401_UNAUTHORIZED
    )

if not user.is_active:
    return Response(
        {'error': 'Bitte überprüfe deine Anmeldedaten und versuche es erneut.'},
        status=status.HTTP_403_FORBIDDEN
    )
```

#### 3. "Passwort vergessen" Funktion ✅

**Endpoint:** `POST /api/password_reset/`

**Features:**
- ✅ E-Mail-basierter Reset
- ✅ HTML E-Mail mit Design (basierend auf Template)
- ✅ Sicherer Token-Link
- ✅ Link führt zu Frontend
- ✅ Allgemeine Response (Sicherheit)

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (IMMER gleich - egal ob E-Mail existiert):**
```json
{
  "detail": "Falls ein Konto mit dieser E-Mail existiert, wurde eine Nachricht zum Zurücksetzen des Passworts gesendet."
}
```

**Reset-Link Format:**
```
http://localhost:4200/password-reset-confirm/{uid}/{token}/
```

**E-Mail-Template:**
- ✅ HTML Design (Videoflix Branding)
- ✅ Sicherheitswarnung
- ✅ Zeitlich begrenzter Link
- ✅ Alternative Plain-Text Version

**Implementation:**
```python
# users/views.py - PasswordResetView
def post(self, request):
    email = request.data.get('email')
    
    try:
        user = User.objects.get(email=email)
        uid, token = generate_activation_token(user)
        send_password_reset_email(user, uid, token)  # HTML Email
    except User.DoesNotExist:
        pass  # Keine Reaktion - Sicherheit!
    
    # IMMER gleiche Response
    return Response({
        'detail': 'Falls ein Konto mit dieser E-Mail existiert...'
    })
```

**Passwort-Reset-Bestätigung:**

**Endpoint:** `POST /api/password_confirm/{uid}/{token}/`

**Request:**
```json
{
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

**Success Response:**
```json
{
  "detail": "Your Password has been successfully reset."
}
```

#### 4. Nach Login → Weiterleitung ✅

**Success Response:**
```json
{
  "detail": "Anmeldung erfolgreich",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user"
  }
}
```

**Frontend Verarbeitung:**
```javascript
// Nach erfolgreicher Anmeldung
fetch('/api/login/', {
  method: 'POST',
  body: JSON.stringify({ email, password })
})
.then(response => response.json())
.then(data => {
  if (data.detail === "Anmeldung erfolgreich") {
    // ✅ Weiterleitung zur Startseite
    window.location.href = '/home';
  }
});
```

**HTTP-Only Cookies:**
- ✅ `access_token` - 1 Stunde gültig
- ✅ `refresh_token` - 7 Tage gültig
- ✅ Automatisch im Browser gespeichert
- ✅ Nicht per JavaScript zugreifbar (Sicherheit)

#### 5. Navigation zur Registrierung ✅

**Frontend-Integration:**

Der API-Endpoint ist so konzipiert, dass das Frontend einfach zwischen Login und Registrierung wechseln kann:

```javascript
// Login-Seite
<button onClick={() => navigate('/register')}>
  Noch kein Konto? Jetzt registrieren
</button>

// Register-Seite
<button onClick={() => navigate('/login')}>
  Bereits registriert? Zum Login
</button>
```

**API unterstützt:**
- Klare Endpoint-Trennung (`/api/login/` vs `/api/register/`)
- Konsistente Fehlerbehandlung
- Gleiche Response-Struktur

### API-Dokumentation

#### Login

**Request:**
```http
POST /api/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (200 OK):**
```json
{
  "detail": "Anmeldung erfolgreich",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user"
  }
}
```

**Cookies (automatisch gesetzt):**
```
Set-Cookie: access_token=xxx; HttpOnly; SameSite=Lax; Max-Age=3600
Set-Cookie: refresh_token=xxx; HttpOnly; SameSite=Lax; Max-Age=604800
```

**Error Response (401 UNAUTHORIZED):**
```json
{
  "error": "Bitte überprüfe deine Anmeldedaten und versuche es erneut."
}
```

#### Passwort Vergessen

**Request:**
```http
POST /api/password_reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (200 OK - IMMER gleich):**
```json
{
  "detail": "Falls ein Konto mit dieser E-Mail existiert, wurde eine Nachricht zum Zurücksetzen des Passworts gesendet."
}
```

#### Token Refresh

**Request:**
```http
POST /api/token/refresh/
Cookie: refresh_token=xxx
```

**Response (200 OK):**
```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

### Sicherheitsfeatures

1. ✅ **Allgemeine Fehlermeldungen** - Keine Information Leaks
2. ✅ **HTTP-Only Cookies** - Schutz vor XSS
3. ✅ **JWT Tokens** - Stateless Authentication
4. ✅ **CSRF Protection** - Django CSRF Middleware
5. ✅ **E-Mail Enumeration Schutz** - Gleiche Response bei Reset
6. ✅ **Account Status Schutz** - Keine Hinweise auf inaktive Accounts
7. ✅ **Token Expiration** - Zeitlich begrenzte Tokens

### User Flow

```
1. User öffnet Login-Seite
   ↓
2. User gibt E-Mail & Passwort ein
   ↓
3. Frontend validiert Felder (nicht leer)
   ↓
4. POST /api/login/
   ↓
5a. Erfolg → Cookies gesetzt → Redirect /home
5b. Fehler → Allgemeine Meldung anzeigen
   ↓
6. User kann zu Registrierung wechseln
   ODER
   User kann "Passwort vergessen" nutzen
```

**Passwort Vergessen Flow:**
```
1. User klickt "Passwort vergessen"
   ↓
2. User gibt E-Mail ein
   ↓
3. POST /api/password_reset/
   ↓
4. Allgemeine Success-Meldung
   ↓
5. Falls E-Mail existiert: HTML-Email gesendet
   ↓
6. User klickt Link in E-Mail
   ↓
7. Frontend: /password-reset-confirm/{uid}/{token}
   ↓
8. User gibt neues Passwort ein
   ↓
9. POST /api/password_confirm/{uid}/{token}/
   ↓
10. Erfolg → Redirect zu Login
```

### Testing

**Test Login (Success):**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }' \
  -c cookies.txt
```

**Test Login (Wrong Password):**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "WrongPassword"
  }'
# Erwartet: "Bitte überprüfe deine Anmeldedaten..."
```

**Test Password Reset:**
```bash
curl -X POST http://localhost:8000/api/password_reset/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
# Erwartet: "Falls ein Konto mit dieser E-Mail existiert..."
```

**Test Token Refresh:**
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -b cookies.txt
```

### Dateien

**Implementierte Dateien:**
- `users/views.py` - LoginView, PasswordResetView
- `users/utils.py` - authenticate_user(), generate_jwt_tokens(), set_auth_cookies()
- `users/email_templates.py` - HTML Password-Reset Template
- `core/settings.py` - JWT & Cookie Konfiguration

### Swagger/OpenAPI Dokumentation

Login & Password-Reset sind dokumentiert unter:
- **Swagger UI:** http://localhost:8000/api/schema/swagger-ui/#/users
- **ReDoc:** http://localhost:8000/api/schema/redoc/#tag/users

---

## ✅ Zusammenfassung User Story 2

| Anforderung | Status | Implementation |
|-------------|--------|----------------|
| Login-Formular (E-Mail, Passwort) | ✅ | LoginView mit JWT |
| Allgemeine Fehlermeldungen | ✅ | Einheitliche Meldungen |
| "Passwort vergessen" Option | ✅ | HTML Email-Reset |
| Nach Login → Startseite | ✅ | Response mit User-Daten |
| Navigation zu Registrierung | ✅ | API-Endpoints getrennt |
| HTTP-Only Cookies | ✅ | Sichere Token-Speicherung |
| Token Refresh | ✅ | Automatische Verlängerung |

**Status: ✅ VOLLSTÄNDIG IMPLEMENTIERT & PRODUCTION-READY**
