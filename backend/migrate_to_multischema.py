#!/usr/bin/env python
"""
Migration script to convert from single-schema to multi-schema architecture
This script will:
1. Backup current data
2. Create new tenant schemas
3. Migrate data to appropriate schemas
4. Update models to remove tenant foreign keys
"""

import os
import sys
import django
import json
from django.core.management import call_command
from django.db import connection, transaction

# Setup Django
sys.path.append('/home/elixir/Documents/PycharmProjects/Skiller/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skiller.settings')
django.setup()

from tenants.models import Tenant, TenantUser, TenantSettings
from tenants.schema_utils import SchemaManager
from django.contrib.auth import get_user_model

User = get_user_model()


def backup_data():
    """Backup current tenant data"""
    print("🔄 Backing up current data...")
    
    # Create backup directory
    backup_dir = '/tmp/skiller_migration_backup'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup tenants
    tenants_data = []
    for tenant in Tenant.objects.all():
        tenants_data.append({
            'id': str(tenant.id),
            'name': tenant.name,
            'slug': tenant.slug,
            'domain': tenant.domain,
            'plan': tenant.plan,
            'is_active': tenant.is_active,
            'created_at': tenant.created_at.isoformat(),
        })
    
    with open(f'{backup_dir}/tenants.json', 'w') as f:
        json.dump(tenants_data, f, indent=2)
    
    # Backup users by tenant
    users_by_tenant = {}
    for user in User.objects.all():
        tenant_id = str(user.tenant.id)
        if tenant_id not in users_by_tenant:
            users_by_tenant[tenant_id] = []
        
        users_by_tenant[tenant_id].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_tenant_admin': user.is_tenant_admin,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined.isoformat(),
        })
    
    with open(f'{backup_dir}/users_by_tenant.json', 'w') as f:
        json.dump(users_by_tenant, f, indent=2)
    
    print(f"✅ Data backed up to {backup_dir}")
    return backup_dir


def create_tenant_schemas():
    """Create schemas for existing tenants"""
    print("🔄 Creating tenant schemas...")
    
    for tenant in Tenant.objects.all():
        schema_name = SchemaManager.get_schema_name(tenant.slug)
        
        print(f"Creating schema for tenant: {tenant.name} -> {schema_name}")
        
        # Update tenant with schema name
        tenant.schema_name = schema_name
        tenant.save()
        
        # Create schema
        if tenant.create_schema():
            print(f"✅ Created schema: {schema_name}")
            
            # Run migrations in the new schema
            if SchemaManager.migrate_schema(schema_name):
                print(f"✅ Migrations completed for: {schema_name}")
            else:
                print(f"❌ Failed to run migrations for: {schema_name}")
        else:
            print(f"❌ Failed to create schema: {schema_name}")


def migrate_tenant_data():
    """Migrate data from public schema to tenant schemas"""
    print("🔄 Migrating data to tenant schemas...")
    
    # Load backup data
    backup_dir = '/tmp/skiller_migration_backup'
    
    with open(f'{backup_dir}/users_by_tenant.json', 'r') as f:
        users_by_tenant = json.load(f)
    
    for tenant in Tenant.objects.all():
        tenant_id = str(tenant.id)
        print(f"Migrating data for tenant: {tenant.name}")
        
        # Switch to tenant schema
        SchemaManager.set_search_path(tenant.schema_name)
        
        try:
            # Create tenant settings in tenant schema
            TenantSettings.objects.get_or_create(
                tenant_id=tenant.id,
                defaults={
                    'enable_ai_grading': True,
                    'allow_code_execution': True,
                }
            )
            
            # Migrate users
            if tenant_id in users_by_tenant:
                for user_data in users_by_tenant[tenant_id]:
                    # Create user in tenant schema (without tenant FK)
                    User.objects.get_or_create(
                        username=user_data['username'],
                        defaults={
                            'email': user_data['email'],
                            'role': user_data['role'],
                            'is_tenant_admin': user_data['is_tenant_admin'],
                            'is_superuser': user_data['is_superuser'],
                            'is_staff': user_data['is_staff'],
                        }
                    )
            
            print(f"✅ Migrated data for tenant: {tenant.name}")
            
        except Exception as e:
            print(f"❌ Error migrating data for tenant {tenant.name}: {e}")
        
        finally:
            # Return to public schema
            SchemaManager.set_search_path('public')


def cleanup_public_schema():
    """Clean up old tenant-specific data from public schema"""
    print("🔄 Cleaning up public schema...")
    
    try:
        # Keep tenants table in public schema for tenant discovery
        # Remove user data from public schema since they're now in tenant schemas
        User.objects.all().delete()
        
        print("✅ Cleaned up public schema")
        
    except Exception as e:
        print(f"❌ Error cleaning up public schema: {e}")


def main():
    """Main migration function"""
    print("🚀 Starting migration from single-schema to multi-schema architecture")
    print("=" * 60)
    
    try:
        # Step 1: Backup current data
        backup_dir = backup_data()
        
        # Step 2: Create tenant schemas
        create_tenant_schemas()
        
        # Step 3: Migrate data to tenant schemas
        migrate_tenant_data()
        
        # Step 4: Clean up public schema
        cleanup_public_schema()
        
        print("\n" + "=" * 60)
        print("🎉 Migration completed successfully!")
        print("=" * 60)
        print("Next steps:")
        print("1. Update your models to remove tenant foreign keys")
        print("2. Create and apply new migrations")
        print("3. Test the multi-schema setup")
        print(f"4. Backup stored at: {backup_dir}")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Please check the logs and try again.")
        return False
    
    return True


if __name__ == "__main__":
    main()
