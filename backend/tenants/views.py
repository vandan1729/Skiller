from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg
from .models import Tenant, TenantUser, TenantSettings
from .serializers import (
    TenantSerializer, TenantUserSerializer, 
    TenantSettingsSerializer, TenantStatsSerializer
)


class TenantViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        return Tenant.objects.filter(id=user.tenant.id)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get tenant statistics"""
        tenant = self.get_object()
        
        # Import here to avoid circular imports
        from interviews.models import Interview
        from candidates.models import Candidate
        from questions.models import Question
        from submissions.models import Submission
        
        stats_data = {
            'total_interviews': Interview.objects.filter(tenant=tenant).count(),
            'active_interviews': Interview.objects.filter(
                tenant=tenant, 
                status='active'
            ).count(),
            'total_candidates': Candidate.objects.filter(tenant=tenant).count(),
            'total_questions': Question.objects.filter(tenant=tenant).count(),
            'completion_rate': 0.0,
            'average_score': 0.0,
        }
        
        # Calculate completion rate
        total_submissions = Submission.objects.filter(tenant=tenant).count()
        completed_submissions = Submission.objects.filter(
            tenant=tenant,
            status='completed'
        ).count()
        
        if total_submissions > 0:
            stats_data['completion_rate'] = completed_submissions / total_submissions
        
        # Calculate average score
        avg_score = Submission.objects.filter(
            tenant=tenant,
            status='completed'
        ).aggregate(avg_score=Avg('total_score'))
        
        stats_data['average_score'] = avg_score['avg_score'] or 0.0
        
        serializer = TenantStatsSerializer(stats_data)
        return Response(serializer.data)


class TenantUserViewSet(viewsets.ModelViewSet):
    serializer_class = TenantUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return TenantUser.objects.none()
        return TenantUser.objects.filter(tenant=tenant)
    
    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            serializer.save(tenant=tenant)


class TenantSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return TenantSettings.objects.none()
        return TenantSettings.objects.filter(tenant=tenant)
    
    def get_object(self):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            settings, created = TenantSettings.objects.get_or_create(tenant=tenant)
            return settings
        return None
