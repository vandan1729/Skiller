"""
PostgreSQL Schema Management Utilities for Multi-Tenant Architecture
"""

import logging
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.db import connection

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages PostgreSQL schemas for multi-tenant architecture"""
    
    @staticmethod
    def get_schema_name(tenant_slug):
        """Generate schema name from tenant slug"""
        return f"tenant_{tenant_slug}"
    
    @staticmethod
    def create_schema(schema_name):
        """Create a new PostgreSQL schema"""
        with connection.cursor() as cursor:
            try:
                # Create schema
                cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
                logger.info(f"Created schema: {schema_name}")
                return True
            except Exception as e:
                logger.error(f"Error creating schema {schema_name}: {e}")
                return False
    
    @staticmethod
    def drop_schema(schema_name):
        """Drop a PostgreSQL schema"""
        with connection.cursor() as cursor:
            try:
                cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
                logger.info(f"Dropped schema: {schema_name}")
                return True
            except Exception as e:
                logger.error(f"Error dropping schema {schema_name}: {e}")
                return False
    
    @staticmethod
    def schema_exists(schema_name):
        """Check if schema exists"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = %s
                )
            """, [schema_name])
            return cursor.fetchone()[0]
    
    @staticmethod
    def set_search_path(schema_name):
        """Set PostgreSQL search_path to use specific schema"""
        with connection.cursor() as cursor:
            cursor.execute(f'SET search_path TO "{schema_name}", public')
            logger.debug(f"Set search_path to: {schema_name}")
    
    @staticmethod
    def get_current_schema():
        """Get current schema from search_path"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_schema()")
            return cursor.fetchone()[0]
        
    @staticmethod
    def get_user_defined_public_apps():
        user_public_apps = []
        project_root = Path(settings.BASE_DIR)
        apps_dir = project_root / 'apps'
        if not apps_dir.is_dir():
            logger.warning(f"Apps directory not found: {apps_dir}")
            return user_public_apps

        user_public_apps = [item.name for item in apps_dir.iterdir() if item.is_dir()]

        return user_public_apps
            
    
    @staticmethod
    def migrate_schema(schema_name, app_labels=None):
        """Run Django migrations for a specific schema"""
        try:
            
            # Set search path to the tenant schema
            SchemaManager.set_search_path(schema_name)
            
            # Run migrations
            if app_labels:
                for app_label in app_labels:
                    call_command('migrate', app_label, verbosity=0, interactive=False)
            else:
                # Get all installed apps except tenants
                tenant_apps = SchemaManager.get_user_defined_public_apps()
                
                for app_label in tenant_apps:
                    try:
                        call_command('migrate', app_label, verbosity=0, interactive=False)
                    except Exception as app_error:
                        logger.warning(f"Could not migrate app {app_label} for schema {schema_name}: {app_error}")
        
            logger.info(f"Migrations completed for schema: {schema_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error running migrations for schema {schema_name}: {e}")
            return False
        finally:
            # Reset to public schema
            SchemaManager.set_search_path('public')
    
    @staticmethod
    def list_tenant_schemas():
        """List all tenant schemas"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT schema_name FROM information_schema.schemata 
                WHERE schema_name LIKE 'tenant_%'
                ORDER BY schema_name
            """)
            return [row[0] for row in cursor.fetchall()]


class TenantSchemaRouter:
    """Database router for schema-based multi-tenancy"""
    
    def __init__(self):
        self.tenant_schema = None
    
    def set_tenant_schema(self, schema_name):
        """Set the current tenant schema"""
        self.tenant_schema = schema_name
        SchemaManager.set_search_path(schema_name)
    
    def clear_tenant_schema(self):
        """Clear tenant schema and return to public"""
        self.tenant_schema = None
        SchemaManager.set_search_path('public')


# Global router instance
schema_router = TenantSchemaRouter()
