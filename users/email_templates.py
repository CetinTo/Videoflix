"""
HTML Email Templates for User Authentication
Based on design templates in EmailTemplates_Backend/
"""


def get_activation_email_html(activation_link, user_email):
    """
    HTML template for account activation email
    Based on: EmailTemplates_Backend/Designvorlage confirm_email Videoflix.png
    """
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aktiviere dein Videoflix-Konto</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Arial', sans-serif;
            background-color: #141414;
            color: #ffffff;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #1a1a1a;
            padding: 40px 20px;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .logo h1 {{
            color: #e50914;
            font-size: 32px;
            margin: 0;
            font-weight: bold;
        }}
        .content {{
            background-color: #2a2a2a;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
        }}
        .content h2 {{
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .content p {{
            color: #b3b3b3;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        .btn {{
            display: inline-block;
            background-color: #e50914;
            color: #ffffff;
            text-decoration: none;
            padding: 15px 40px;
            border-radius: 4px;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s;
        }}
        .btn:hover {{
            background-color: #c40812;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #808080;
            font-size: 12px;
        }}
        .divider {{
            border-top: 1px solid #404040;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="logo">
            <h1>VIDEOFLIX</h1>
        </div>
        
        <div class="content">
            <h2>Willkommen bei Videoflix!</h2>
            <p>
                Vielen Dank für deine Registrierung. Um dein Konto zu aktivieren und 
                Zugang zu tausenden von Filmen und Serien zu erhalten, klicke bitte 
                auf den folgenden Button:
            </p>
            
            <a href="{activation_link}" class="btn">Konto aktivieren</a>
            
            <div class="divider"></div>
            
            <p style="font-size: 14px; color: #999999;">
                Falls der Button nicht funktioniert, kopiere diesen Link in deinen Browser:<br>
                <a href="{activation_link}" style="color: #e50914; word-break: break-all;">{activation_link}</a>
            </p>
            
            <p style="font-size: 14px; color: #999999;">
                Diese E-Mail wurde an <strong>{user_email}</strong> gesendet.
            </p>
        </div>
        
        <div class="footer">
            <p>
                © 2026 Videoflix. Alle Rechte vorbehalten.<br>
                Diese E-Mail wurde automatisch generiert. Bitte antworte nicht darauf.
            </p>
        </div>
    </div>
</body>
</html>
    """


def get_password_reset_email_html(reset_link, user_email):
    """
    HTML template for password reset email
    Based on: EmailTemplates_Backend/Designvorlage password_reset Videoflix.png
    """
    return f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Passwort zurücksetzen - Videoflix</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Arial', sans-serif;
            background-color: #141414;
            color: #ffffff;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #1a1a1a;
            padding: 40px 20px;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .logo h1 {{
            color: #e50914;
            font-size: 32px;
            margin: 0;
            font-weight: bold;
        }}
        .content {{
            background-color: #2a2a2a;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
        }}
        .content h2 {{
            color: #ffffff;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .content p {{
            color: #b3b3b3;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        .btn {{
            display: inline-block;
            background-color: #e50914;
            color: #ffffff;
            text-decoration: none;
            padding: 15px 40px;
            border-radius: 4px;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s;
        }}
        .btn:hover {{
            background-color: #c40812;
        }}
        .warning {{
            background-color: #3a2a1a;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin: 20px 0;
            text-align: left;
        }}
        .warning p {{
            margin: 0;
            font-size: 14px;
            color: #ffb74d;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #808080;
            font-size: 12px;
        }}
        .divider {{
            border-top: 1px solid #404040;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="logo">
            <h1>VIDEOFLIX</h1>
        </div>
        
        <div class="content">
            <h2>Passwort zurücksetzen</h2>
            <p>
                Du hast eine Anfrage zum Zurücksetzen deines Passworts gestellt. 
                Klicke auf den folgenden Button, um ein neues Passwort festzulegen:
            </p>
            
            <a href="{reset_link}" class="btn">Neues Passwort festlegen</a>
            
            <div class="warning">
                <p>
                    <strong>⚠️ Wichtig:</strong> Dieser Link ist aus Sicherheitsgründen 
                    nur für kurze Zeit gültig. Falls du diese Anfrage nicht gestellt hast, 
                    ignoriere diese E-Mail einfach.
                </p>
            </div>
            
            <div class="divider"></div>
            
            <p style="font-size: 14px; color: #999999;">
                Falls der Button nicht funktioniert, kopiere diesen Link in deinen Browser:<br>
                <a href="{reset_link}" style="color: #e50914; word-break: break-all;">{reset_link}</a>
            </p>
            
            <p style="font-size: 14px; color: #999999;">
                Diese E-Mail wurde an <strong>{user_email}</strong> gesendet.
            </p>
        </div>
        
        <div class="footer">
            <p>
                © 2026 Videoflix. Alle Rechte vorbehalten.<br>
                Diese E-Mail wurde automatisch generiert. Bitte antworte nicht darauf.
            </p>
            <p style="margin-top: 10px;">
                Hast du Fragen? Besuche unser <a href="http://localhost:4200/help" style="color: #e50914;">Hilfe-Center</a>
            </p>
        </div>
    </div>
</body>
</html>
    """


def get_activation_email_text(activation_link):
    """Plain text version of activation email"""
    return f"""
Willkommen bei Videoflix!

Vielen Dank für deine Registrierung. Um dein Konto zu aktivieren, 
klicke bitte auf den folgenden Link:

{activation_link}

Falls der Link nicht funktioniert, kopiere ihn in deinen Browser.

Mit freundlichen Grüßen
Dein Videoflix Team

---
© 2026 Videoflix. Alle Rechte vorbehalten.
Diese E-Mail wurde automatisch generiert.
    """


def get_password_reset_email_text(reset_link):
    """Plain text version of password reset email"""
    return f"""
Passwort zurücksetzen - Videoflix

Du hast eine Anfrage zum Zurücksetzen deines Passworts gestellt.
Klicke auf den folgenden Link, um ein neues Passwort festzulegen:

{reset_link}

WICHTIG: Dieser Link ist aus Sicherheitsgründen nur für kurze Zeit gültig.
Falls du diese Anfrage nicht gestellt hast, ignoriere diese E-Mail einfach.

Mit freundlichen Grüßen
Dein Videoflix Team

---
© 2026 Videoflix. Alle Rechte vorbehalten.
Diese E-Mail wurde automatisch generiert.
    """
