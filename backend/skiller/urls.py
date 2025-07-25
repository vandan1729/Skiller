"""skiller URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API endpoints
    path('api/auth/', include('tenant_apps.authentication.urls')),
    path('api/tenants/', include('public_apps.tenants.urls')),
    path('api/interviews/', include('tenant_apps.interviews.urls')),
    path('api/questions/', include('tenant_apps.questions.urls')),
    path('api/submissions/', include('tenant_apps.submissions.urls')),
    path('api/grading/', include('tenant_apps.grading.urls')),
    path('api/candidates/', include('tenant_apps.candidates.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
