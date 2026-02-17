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
    lookup_field = 'page_type'
    
    def get_queryset(self):
        """Returns only published legal pages"""
        return LegalPage.objects.filter(is_published=True)
    
    @extend_schema(
        description='Returns privacy policy page'
    )
    @action(detail=False, methods=['get'])
    def privacy(self, request):
        """Returns privacy policy content"""
        try:
            page = LegalPage.objects.get(
                page_type='privacy',
                is_published=True
            )
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        except LegalPage.DoesNotExist:
            return Response(
                {'detail': 'Privacy policy not found'},
                status=404
            )
    
    @extend_schema(
        description='Returns imprint page'
    )
    @action(detail=False, methods=['get'])
    def imprint(self, request):
        """Returns imprint content"""
        try:
            page = LegalPage.objects.get(
                page_type='imprint',
                is_published=True
            )
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        except LegalPage.DoesNotExist:
            return Response(
                {'detail': 'Imprint not found'},
                status=404
            )
    
    @extend_schema(
        description='Returns terms of service page'
    )
    @action(detail=False, methods=['get'])
    def terms(self, request):
        """Returns terms of service content"""
        try:
            page = LegalPage.objects.get(
                page_type='terms',
                is_published=True
            )
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        except LegalPage.DoesNotExist:
            return Response(
                {'detail': 'Terms of service not found'},
                status=404
            )
