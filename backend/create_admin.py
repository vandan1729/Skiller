#!/usr/bin/env python
"""
Script to create a tenant and superuser for the Skiller multi-tenant platform
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/elixir/Documents/PycharmProjects/Skiller/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skiller.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant, TenantSettings
from django.db import transaction

def create_tenant_and_superuser():
    User = get_user_model()
    
    try:
        with transaction.atomic():
            # Create tenant
            print("Creating tenant...")
            tenant = Tenant.objects.create(
                name="Admin Organization",
                slug="admin-org",
                is_active=True,
                plan="enterprise",
                allow_public_signup=False,
                max_interviews=1000,
                max_questions=1000,
                max_candidates=1000
            )
            print(f"✓ Created tenant: {tenant.name}")
            
            # Tenant settings are automatically created by signal
            print("✓ Tenant settings created automatically by signal")
            
            # Create superuser
            print("Creating superuser...")
            user = User.objects.create_user(
                username="admin",
                email="admin@skiller.com",
                password="admin123",  # You can change this later
                tenant=tenant,
                role="admin",
                is_tenant_admin=True,
                is_staff=True,
                is_superuser=True,
                can_create_interviews=True,
                can_manage_questions=True,
                can_view_analytics=True,
                can_manage_users=True
            )
            print(f"✓ Created superuser: {user.username}")
            
            print("\n" + "="*50)
            print("SUCCESS! Tenant and superuser created successfully")
            print("="*50)
            print(f"Tenant: {tenant.name} (slug: {tenant.slug})")
            print(f"Superuser: {user.username}")
            print(f"Email: {user.email}")
            print("Password: admin123")
            print("\nYou can now log in to the Django admin at http://127.0.0.1:8000/admin/")
            print("="*50)
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    create_tenant_and_superuser()
