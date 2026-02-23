from rest_framework import serializers
from .models import LegalPage


class LegalPageSerializer(serializers.ModelSerializer):
    """Serializer for legal pages"""
    
    page_type_display = serializers.CharField(
        source='get_page_type_display',
        read_only=True
    )
    
    class Meta:
        model = LegalPage
        fields = [
            'id',
            'page_type',
            'page_type_display',
            'language',
            'title',
            'content',
            'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']
