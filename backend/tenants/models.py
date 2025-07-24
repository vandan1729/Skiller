from django.db import models
from django.contrib.auth.models import AbstractUser
from .schema_utils import SchemaManager
import uuid


class Tenant(models.Model):
    """Company/Organization model for multi-tenancy"""
    
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    schema_name = models.CharField(max_length=63, unique=True, editable=False)  # PostgreSQL schema name
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    logo = models.ImageField(upload_to='tenant_logos/', null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Subscription details
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    
    # Settings
    allow_public_signup = models.BooleanField(default=False)
    max_interviews = models.IntegerField(default=10)
    max_questions = models.IntegerField(default=50)
    max_candidates = models.IntegerField(default=100)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenants'
        
    def save(self, *args, **kwargs):
        # Auto-generate schema name from slug
        if not self.schema_name:
            self.schema_name = SchemaManager.get_schema_name(self.slug)
        super().save(*args, **kwargs)
        
    def create_schema(self):
        """Create PostgreSQL schema for this tenant"""
        return SchemaManager.create_schema(self.schema_name)
    
    def drop_schema(self):
        """Drop PostgreSQL schema for this tenant"""
        return SchemaManager.drop_schema(self.schema_name)
    
    def schema_exists(self):
        """Check if tenant's schema exists"""
        return SchemaManager.schema_exists(self.schema_name)
        
    def __str__(self):
        return self.name


class TenantUser(AbstractUser):
    """Extended User model with tenant relationship - NO tenant FK needed with schema-based approach"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('recruiter', 'Recruiter'),
        ('interviewer', 'Interviewer'),
        ('viewer', 'Viewer'),
    ]
    
    # NOTE: No tenant ForeignKey needed - isolation is at schema level
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recruiter')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='user_avatars/', null=True, blank=True)
    is_tenant_admin = models.BooleanField(default=False)
    
    # Override groups and user_permissions with custom related_names to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='tenant_users',
        related_query_name='tenant_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='tenant_users',
        related_query_name='tenant_user',
    )
    
    # Permissions
    can_create_interviews = models.BooleanField(default=True)
    can_manage_questions = models.BooleanField(default=True)
    can_view_analytics = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'tenant_users'
        # Remove unique_together constraint since no tenant field
        
    def __str__(self):
        return f"{self.username}"


class TenantSettings(models.Model):
    """Tenant-specific configuration - stored in tenant's schema"""
    
    # Use UUID instead of ForeignKey since we're in separate schemas
    tenant_id = models.UUIDField(unique=True)  # Reference to tenant in public schema
    
    # Branding
    primary_color = models.CharField(max_length=7, default='#007bff')
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    custom_css = models.TextField(blank=True)
    
    # Email settings
    from_email = models.EmailField(blank=True)
    email_signature = models.TextField(blank=True)
    
    # Interview settings
    default_interview_duration = models.IntegerField(default=60)  # minutes
    allow_code_execution = models.BooleanField(default=True)
    require_webcam = models.BooleanField(default=False)
    auto_submit_on_time_end = models.BooleanField(default=True)
    
    # Grading settings
    enable_ai_grading = models.BooleanField(default=True)
    ai_grading_model = models.CharField(max_length=50, default='gpt-3.5-turbo')
    manual_review_threshold = models.FloatField(default=0.7)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenant_settings'
