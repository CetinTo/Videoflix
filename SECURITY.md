# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please email: **security@videoflix.com**

**Please do not create public issues for security vulnerabilities.**

## Security Best Practices

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY` (64+ random characters)
- [ ] Configure strong database passwords
- [ ] Enable HTTPS only
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Configure CORS correctly
- [ ] Enable CSRF protection
- [ ] Use HTTP-Only cookies
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Database backups
- [ ] Log monitoring

### Environment Variables

Never commit sensitive data:
- Database credentials
- SECRET_KEY
- Email passwords
- API keys

### Django Security Settings

```python
# Production settings.py
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Database Security

- Use PostgreSQL user with limited permissions
- Regular backups
- Encrypted connections
- Strong passwords

### File Upload Security

- Validate file types
- Limit file sizes
- Scan for malware (production)
- Store uploads outside web root

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Updates

Check regularly for:
- Django security releases
- Python vulnerabilities
- Dependency updates

```bash
pip list --outdated
```
