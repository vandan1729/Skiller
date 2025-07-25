from rest_framework import serializers
from .models import Tenant, TenantUser, TenantSettings


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'domain', 'logo', 'description',
            'plan', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TenantUserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = TenantUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'avatar', 'is_tenant_admin',
            'tenant', 'tenant_name', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'tenant_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class TenantSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSettings
        fields = [
            'primary_color', 'secondary_color', 'custom_css',
            'from_email', 'email_signature',
            'default_interview_duration', 'allow_code_execution',
            'require_webcam', 'auto_submit_on_time_end',
            'enable_ai_grading', 'ai_grading_model',
            'manual_review_threshold'
        ]


class TenantStatsSerializer(serializers.Serializer):
    """Statistics for tenant dashboard"""
    total_interviews = serializers.IntegerField()
    active_interviews = serializers.IntegerField()
    total_candidates = serializers.IntegerField()
    total_questions = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_score = serializers.FloatField()
