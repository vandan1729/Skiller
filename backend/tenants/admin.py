from django.contrib import admin
from .models import Tenant, TenantUser, TenantSettings


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'schema_name', 'plan', 'is_active', 'created_at']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'domain']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['schema_name']


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(TenantSettings)
class TenantSettingsAdmin(admin.ModelAdmin):
    list_display = ['tenant_id', 'enable_ai_grading', 'default_interview_duration']
    list_filter = ['enable_ai_grading', 'require_webcam']
