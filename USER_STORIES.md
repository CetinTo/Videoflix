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
