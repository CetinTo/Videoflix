from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LegalPageViewSet

router = DefaultRouter()
router.register(r'legal', LegalPageViewSet, basename='legal')

urlpatterns = [
    path('', include(router.urls)),
]
