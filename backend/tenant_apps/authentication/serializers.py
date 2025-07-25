from rest_framework import serializers
from public_apps.tenants.models import TenantUser, Tenant


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    tenant_slug = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        tenant_slug = attrs.get('tenant_slug')
        
        if not all([username, password, tenant_slug]):
            raise serializers.ValidationError('All fields are required')
        
        try:
            tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
        except Tenant.DoesNotExist:
            raise serializers.ValidationError('Invalid tenant')
        
        try:
            user = TenantUser.objects.get(
                username=username,
                tenant=tenant,
                is_active=True
            )
            
            if not user.check_password(password):
                raise serializers.ValidationError('Invalid credentials')
                
        except TenantUser.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')
        
        attrs['user'] = user
        attrs['tenant'] = tenant
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    tenant_slug = serializers.CharField(write_only=True)
    
    class Meta:
        model = TenantUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'tenant_slug'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError('Passwords do not match')
        
        tenant_slug = attrs.pop('tenant_slug')
        try:
            tenant = Tenant.objects.get(slug=tenant_slug, is_active=True)
            if not tenant.allow_public_signup:
                raise serializers.ValidationError('Registration not allowed for this tenant')
        except Tenant.DoesNotExist:
            raise serializers.ValidationError('Invalid tenant')
        
        attrs['tenant'] = tenant
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        tenant = validated_data.pop('tenant')
        
        user = TenantUser.objects.create_user(
            tenant=tenant,
            **validated_data
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = TenantUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'avatar', 'tenant_name',
            'can_create_interviews', 'can_manage_questions',
            'can_view_analytics', 'can_manage_users'
        ]
        read_only_fields = ['id', 'username', 'tenant_name']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError('New passwords do not match')
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Invalid old password')
        return value
