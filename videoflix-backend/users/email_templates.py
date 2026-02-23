"""
HTML Email Templates for User Authentication
Based on design templates in EmailTemplates_Backend/
"""


def get_activation_email_html(activation_link, user_email, user_name='User'):
    """
    HTML template for account activation email.
    Button: #2e3edf, border-radius 40px. Variables: username -> user_name, verification_link -> activation_link.
    """
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirm your email</title>
    <style type="text/css">
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 40px 24px;
        }}
        .logo-heading {{
            text-align: center;
            margin-bottom: 28px;
        }}
        .logo-heading .logo-text {{
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 0.02em;
            font-family: Arial, sans-serif;
            vertical-align: middle;
        }}
        .email-container p {{
            font-size: 16px;
            line-height: 1.6;
            color: #333;
            margin: 0 0 16px 0;
        }}
        .btn-default {{
            display: inline-block !important;
            background-color: #2e3edf;
            color: white;
            padding: 12px 24px;
            font-size: 18px;
            font-weight: 400;
            border-radius: 40px;
            border-width: 0;
            transition: background-color 0.3s ease;
            width: auto !important;
            text-decoration: none;
            margin: 12px 0;
        }}
        .btn-default:hover {{
            cursor: pointer;
            background-color: #463eff;
        }}
        .footer {{
            margin-top: 32px;
            font-size: 12px;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="logo-heading">
            <span class="logo-text" style="color:#5b21b6;">VIDEOFLIX</span>
        </div>

        <p>Dear {user_name},</p>

        <p>Thank you for registering for <a href="#" style="color:#2e3edf; text-decoration:none;">Videoflix</a>. To complete your registration and verify your email address, please click the button below:</p>

        <a href="{activation_link}" class="btn-default" style="display:inline-block !important; background-color:#2e3edf; color:white !important; padding:12px 24px; font-size:18px; font-weight:400; border-radius:40px; border-width:0; width:auto !important; text-decoration:none; margin:12px 0;">Activate account</a>

        <p>If you did not create an account with us, please disregard this email.<br><br /></p>

        <p>Best regards,</p>

        <p>Your Videoflix Team</p>

        <p class="footer">This email was sent to {user_email}. &copy; Videoflix.</p>
    </div>
</body>
</html>
    """


def get_password_reset_email_html(reset_link, user_email):
    """
    HTML template for password reset email.
    Design: "Reset your Password" – Designvorlage Videoflix (blue button, logo at bottom).
    """
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset your Password</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 40px 24px;
        }}
        .content {{
            padding: 0 16px;
        }}
        .content p {{
            font-size: 16px;
            line-height: 1.6;
            color: #333;
            margin-bottom: 20px;
        }}
        .btn-wrap {{
            text-align: center;
            margin: 24px 0;
        }}
        .btn {{
            display: inline-block;
            background-color: #3367D6;
            color: #ffffff !important;
            text-decoration: none;
            padding: 14px 36px;
            border-radius: 24px;
            font-size: 16px;
            font-weight: bold;
        }}
        .security-note {{
            font-size: 15px;
            color: #555;
            margin: 20px 0;
        }}
        .disclaimer {{
            font-size: 14px;
            color: #666;
            margin-top: 24px;
        }}
        .closing {{
            margin-top: 28px;
            font-size: 16px;
            color: #333;
        }}
        .logo {{
            margin-top: 36px;
            padding-top: 24px;
            border-top: 1px solid #eee;
            text-align: center;
        }}
        .logo-inner {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .logo-icon {{
            color: #6b21a8;
            font-size: 24px;
            line-height: 1;
        }}
        .logo-text {{
            color: #6b21a8;
            font-size: 22px;
            font-weight: bold;
            letter-spacing: 0.05em;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="content">
            <p>Hello,</p>
            <p>We recently received a request to reset your password. If you made this request, please click on the following link to reset your password:</p>

            <div class="btn-wrap">
                <a href="{reset_link}" class="btn" style="display:inline-block; background-color:#3367D6; color:#ffffff !important; text-decoration:none; padding:14px 36px; border-radius:24px; font-size:16px; font-weight:bold;">Reset password</a>
            </div>

            <p class="security-note">Please note that for security reasons, this link is only valid for 24 hours.</p>

            <p class="disclaimer">If you did not request a password reset, please ignore this email.</p>

            <p class="closing">Best regards,<br>Your Videoflix team!</p>

            <div class="logo">
                <div class="logo-inner">
                    <span class="logo-icon" style="color:#6b21a8; font-size:24px;">&#9654;</span>
                    <span class="logo-text" style="color:#6b21a8; font-size:22px; font-weight:bold; letter-spacing:0.05em;">VIDEOFLIX</span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """


def get_activation_email_text(activation_link, user_name='User'):
    """Plain text version of activation email"""
    return f"""
Confirm your email

Dear {user_name},

Thank you for registering with Videoflix.
To complete your registration and verify your email address, please click the link below:

{activation_link}

If you did not create an account with us, please disregard this email.

Best regards,
Your Videoflix Team

---
This email was sent by Videoflix. Please do not reply.
    """


def get_password_reset_email_text(reset_link):
    """Plain text version of password reset email"""
    return f"""
Reset your Password

Hello,

We recently received a request to reset your password. If you made this request, please click on the following link to reset your password:

{reset_link}

Please note that for security reasons, this link is only valid for 24 hours.

If you did not request a password reset, please ignore this email.

Best regards,
Your Videoflix team!

---
This email was sent by Videoflix. Please do not reply.
    """
