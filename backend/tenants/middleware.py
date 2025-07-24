from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from .models import Tenant
from .schema_utils import SchemaManager, schema_router
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to determine tenant and set PostgreSQL schema based on:
    1. Subdomain (tenant.example.com)
    2. Custom domain (tenant.com)
    3. URL path (/tenant/slug/)
    4. Header (X-Tenant-Slug)
    """
    
    def process_request(self, request):
        # Skip tenant resolution for admin and API documentation
        if request.path.startswith('/admin/') or request.path.startswith('/api/schema/'):
            # Use public schema for admin
            SchemaManager.set_search_path('public')
            request.tenant = None
            return None
        
        tenant = None
        
        try:
            # Method 1: Check for custom domain
            host = request.get_host().split(':')[0].lower()
            try:
                tenant = Tenant.objects.filter(domain=host, is_active=True).first()
            except:
                pass  # Database might not be migrated yet
            
            # Method 2: Check for subdomain
            if not tenant and '.' in host:
                subdomain = host.split('.')[0]
                if subdomain != 'www':
                    try:
                        tenant = Tenant.objects.filter(slug=subdomain, is_active=True).first()
                    except:
                        pass
            
            # Method 3: Check URL path pattern /tenant/slug/
            if not tenant and request.path.startswith('/tenant/'):
                path_parts = request.path.strip('/').split('/')
                if len(path_parts) > 1:
                    tenant_slug = path_parts[1]
                    try:
                        tenant = Tenant.objects.filter(slug=tenant_slug, is_active=True).first()
                    except:
                        pass
            
            # Method 4: Check X-Tenant-Slug header
            if not tenant:
                tenant_slug = request.META.get('HTTP_X_TENANT_SLUG')
                if tenant_slug:
                    try:
                        tenant = Tenant.objects.filter(slug=tenant_slug, is_active=True).first()
                    except:
                        pass
            
            # Set tenant and schema
            if tenant:
                # Verify schema exists
                if not tenant.schema_exists():
                    logger.warning(f"Schema {tenant.schema_name} does not exist for tenant {tenant.slug}")
                    raise Http404(f"Tenant {tenant.slug} is not properly configured")
                
                # Set PostgreSQL schema
                schema_router.set_tenant_schema(tenant.schema_name)
                request.tenant = tenant
                
                logger.debug(f"Tenant resolved: {tenant.slug} -> schema: {tenant.schema_name}")
            else:
                # No tenant found - use public schema
                SchemaManager.set_search_path('public')
                request.tenant = None
                
                # For API endpoints, this might be an error
                if request.path.startswith('/api/') and not request.path.startswith('/api/auth/'):
                    logger.warning(f"No tenant found for request: {request.get_host()}{request.path}")
                
        except Exception as e:
            logger.error(f"Error in TenantMiddleware: {e}")
            # Fallback to public schema
            SchemaManager.set_search_path('public')
            request.tenant = None
    
    def process_response(self, request, response):
        # Reset to public schema after request
        try:
            schema_router.clear_tenant_schema()
        except:
            pass  # Ignore errors during cleanup
        return response
    
    def process_exception(self, request, exception):
        # Reset to public schema on exception
        try:
            schema_router.clear_tenant_schema()
        except:
            pass  # Ignore errors during cleanup
        return None
