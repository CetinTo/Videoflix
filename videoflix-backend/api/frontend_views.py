"""
Serve frontend static files (HTML, CSS, JS, assets) with correct MIME types.
Used when the frontend is loaded from the backend (port 8000) to avoid
Live Server / MIME type issues.
"""
import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse


def _get_frontend_root():
    """Frontend root: FRONTEND_ROOT in Docker, else parent of backend."""
    root = getattr(settings, 'FRONTEND_ROOT', None)
    if root:
        return Path(root)
    return settings.BASE_DIR.parent


def _mime_type(path: Path) -> str:
    """Return MIME type for path."""
    suffix = path.suffix.lower()
    mime_map = {
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.html': 'text/html',
        '.json': 'application/json',
        '.svg': 'image/svg+xml',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.ico': 'image/x-icon',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
    }
    return mime_map.get(suffix) or mimetypes.guess_type(str(path))[0] or 'application/octet-stream'


def serve_frontend_index(request):
    """Serve index.html at root."""
    return serve_frontend_file(request, 'index.html')


def serve_frontend_file(request, path: str):
    """Serve a single frontend file with correct MIME type."""
    if '..' in path or path.startswith('/'):
        raise Http404()
    path = path.strip('/')

    frontend_root = _get_frontend_root()
    file_path = (frontend_root / path).resolve()
    if not str(file_path).startswith(str(frontend_root.resolve())):
        raise Http404()

    if not file_path.exists() or not file_path.is_file():
        raise Http404()

    if not file_path.suffix:
        raise Http404()

    content_type = _mime_type(file_path)
    with open(file_path, 'rb') as f:
        return HttpResponse(f.read(), content_type=content_type)
