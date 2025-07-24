from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from tenants.models import Tenant, TenantSettings
from tenants.schema_utils import SchemaManager
import getpass
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create a superuser with tenant schema for multi-tenant setup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            dest='username',
            help='Username for the superuser',
        )
        parser.add_argument(
            '--email',
            dest='email',
            help='Email for the superuser',
        )
        parser.add_argument(
            '--tenant-name',
            dest='tenant_name',
            help='Name of the tenant organization',
        )
        parser.add_argument(
            '--tenant-slug',
            dest='tenant_slug',
            help='Slug for the tenant (used in URLs)',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get tenant information
        tenant_name = options.get('tenant_name')
        if not tenant_name:
            tenant_name = input('Tenant/Organization name: ')
        
        tenant_slug = options.get('tenant_slug')
        if not tenant_slug:
            tenant_slug = input('Tenant slug (used in URLs): ')
        
        # Get user information
        username = options.get('username')
        if not username:
            username = input('Username: ')
        
        email = options.get('email')
        if not email:
            email = input('Email address: ')
        
        password = getpass.getpass('Password: ')
        password_confirm = getpass.getpass('Password (again): ')
        
        if password != password_confirm:
            self.stdout.write(
                self.style.ERROR('Passwords do not match!')
            )
            return
        
        try:
            with transaction.atomic():
                # Create tenant (this will trigger schema creation via signals)
                self.stdout.write('Creating tenant...')
                tenant = Tenant.objects.create(
                    name=tenant_name,
                    slug=tenant_slug,
                    is_active=True,
                    plan='enterprise'  # Give superuser tenant enterprise plan
                )
                
                self.stdout.write(f'✓ Created tenant: {tenant.name}')
                self.stdout.write(f'✓ Schema created: {tenant.schema_name}')
                
                # Wait for schema creation to complete
                if not tenant.schema_exists():
                    self.stdout.write(
                        self.style.ERROR(f'Schema {tenant.schema_name} was not created successfully!')
                    )
                    return
                
                # Switch to tenant schema to create superuser
                self.stdout.write('Creating superuser in tenant schema...')
                SchemaManager.set_search_path(tenant.schema_name)
                
                try:
                    # Create superuser in tenant schema
                    user = User.objects.create_superuser(
                        username=username,
                        email=email,
                        password=password,
                        role='admin',
                        is_tenant_admin=True,
                        can_create_interviews=True,
                        can_manage_questions=True,
                        can_view_analytics=True,
                        can_manage_users=True,
                    )
                    
                    self.stdout.write(f'✓ Created superuser: {user.username}')
                    
                finally:
                    # Always return to public schema
                    SchemaManager.set_search_path('public')
                
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('=' * 50))
                self.stdout.write(self.style.SUCCESS('SUCCESS! Tenant and superuser created'))
                self.stdout.write(self.style.SUCCESS('=' * 50))
                self.stdout.write(f'Tenant: {tenant.name}')
                self.stdout.write(f'Slug: {tenant.slug}')
                self.stdout.write(f'Schema: {tenant.schema_name}')
                self.stdout.write(f'Superuser: {username}')
                self.stdout.write(f'Email: {email}')
                self.stdout.write('')
                self.stdout.write('Access your tenant at:')
                self.stdout.write(f'- http://{tenant.slug}.localhost:8000/')
                self.stdout.write(f'- http://localhost:8000/tenant/{tenant.slug}/')
                self.stdout.write('=' * 50)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating tenant and superuser: {e}')
            )
            logger.error(f'Error in create_tenant_superuser: {e}', exc_info=True)
