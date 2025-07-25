from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, TenantUserViewSet, TenantSettingsViewSet

router = DefaultRouter()
router.register(r'', TenantViewSet, basename='tenant')
router.register(r'users', TenantUserViewSet, basename='tenant-user')
router.register(r'settings', TenantSettingsViewSet, basename='tenant-settings')

urlpatterns = [
    path('', include(router.urls)),
]
