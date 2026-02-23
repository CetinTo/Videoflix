from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import LegalPage
from .serializers import LegalPageSerializer


@extend_schema_view(
    list=extend_schema(
        description='Returns all published legal pages'
    ),
    retrieve=extend_schema(
        description='Returns specific legal page by ID'
    )
)
class LegalPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for legal pages (Privacy Policy, Imprint, Terms)
    
    Read-only access to legal information pages
    """
    serializer_class = LegalPageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Returns only published legal pages"""
        return LegalPage.objects.filter(is_published=True)
    
    def _get_page(self, page_type, lang):
        """Return published LegalPage for page_type and lang, or None."""
        lang = lang if lang in ('de', 'en') else 'de'
        return LegalPage.objects.filter(
            page_type=page_type,
            language=lang,
            is_published=True
        ).first()

    def _legal_page_response(self, request, page_type, not_found_detail):
        """Return serialized legal page for ?lang= or 404."""
        lang = request.query_params.get('lang', 'de')
        page = self._get_page(page_type, lang)
        if not page:
            return Response({'detail': not_found_detail}, status=404)
        return Response(self.get_serializer(page).data)

    @extend_schema(
        description='Returns privacy policy page. Query: ?lang=de|en (default: de)'
    )
    @action(detail=False, methods=['get'])
    def privacy(self, request):
        """Returns privacy policy content (DE or EN)."""
        return self._legal_page_response(request, 'privacy', 'Privacy policy not found')

    @extend_schema(
        description='Returns imprint page. Query: ?lang=de|en (default: de)'
    )
    @action(detail=False, methods=['get'])
    def imprint(self, request):
        """Returns imprint content (DE or EN)."""
        return self._legal_page_response(request, 'imprint', 'Imprint not found')

    @extend_schema(
        description='Returns terms of service page. Query: ?lang=de|en (default: de)'
    )
    @action(detail=False, methods=['get'])
    def terms(self, request):
        """Returns terms of service content (DE or EN)."""
        return self._legal_page_response(request, 'terms', 'Terms of service not found')
