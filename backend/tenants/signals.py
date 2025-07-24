from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Tenant, TenantSettings
from .schema_utils import SchemaManager
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Tenant)
def create_tenant_schema_and_settings(sender, instance, created, **kwargs):
    """Create schema and default settings when a new tenant is created"""
    if created:
        try:
            # Create PostgreSQL schema for the tenant
            if instance.create_schema():
                logger.info(f"Created schema for tenant: {instance.name}")
                
                # Run migrations in the new schema
                if SchemaManager.migrate_schema(instance.schema_name):
                    logger.info(f"Migrations completed for tenant: {instance.name}")
                    
                    # Switch to tenant schema and create settings
                    SchemaManager.set_search_path(instance.schema_name)
                    try:
                        TenantSettings.objects.create(tenant_id=instance.id)
                        logger.info(f"Created settings for tenant: {instance.name}")
                    except Exception as e:
                        logger.error(f"Error creating settings for tenant {instance.name}: {e}")
                    finally:
                        # Always return to public schema
                        SchemaManager.set_search_path('public')
                else:
                    logger.error(f"Failed to run migrations for tenant: {instance.name}")
            else:
                logger.error(f"Failed to create schema for tenant: {instance.name}")
                
        except Exception as e:
            logger.error(f"Error in tenant creation process for {instance.name}: {e}")


@receiver(post_delete, sender=Tenant)
def delete_tenant_schema(sender, instance, **kwargs):
    """Delete tenant schema when tenant is deleted"""
    try:
        if instance.drop_schema():
            logger.info(f"Deleted schema for tenant: {instance.name}")
        else:
            logger.error(f"Failed to delete schema for tenant: {instance.name}")
    except Exception as e:
        logger.error(f"Error deleting schema for tenant {instance.name}: {e}")
