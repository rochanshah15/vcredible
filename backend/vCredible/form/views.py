from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import CompanyApplication, ApplicationDocument, ApplicationStatusHistory
from .serializers import (
    CompanyApplicationSerializer, 
    CompanyApplicationDetailSerializer,
    ApplicationDocumentSerializer,
    ApplicationStatusHistorySerializer
)

class CompanyApplicationCreateView(generics.CreateAPIView):
    """Create a new company application"""
    
    queryset = CompanyApplication.objects.all()
    serializer_class = CompanyApplicationSerializer
    permission_classes = []  # Allow unauthenticated submissions
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # For authenticated users, check for existing applications
        if request.user.is_authenticated:
            existing_application = CompanyApplication.objects.filter(
                user=request.user,
                application_status__in=['pending', 'under_review']
            ).first()
            
            if existing_application:
                return Response({
                    'error': 'You already have a pending application. Please wait for it to be processed.',
                    'existing_application_id': existing_application.id
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the application
        with transaction.atomic():
            # Save with user if authenticated, otherwise save without user
            if request.user.is_authenticated:
                application = serializer.save(user=request.user)
                changed_by = request.user
            else:
                application = serializer.save(user=None)
                changed_by = None
            
            # Create initial status history
            ApplicationStatusHistory.objects.create(
                application=application,
                old_status='',
                new_status='pending',
                changed_by=changed_by,
                change_reason='Application submitted'
            )
        
        return Response({
            'message': 'Application submitted successfully!',
            'application_id': application.id,
            'status': application.application_status
        }, status=status.HTTP_201_CREATED)

class CompanyApplicationListView(generics.ListAPIView):
    """List all applications for the current user"""
    
    serializer_class = CompanyApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CompanyApplication.objects.filter(user=self.request.user)

class CompanyApplicationDetailView(generics.RetrieveAPIView):
    """Get detailed view of a specific application"""
    
    serializer_class = CompanyApplicationDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CompanyApplication.objects.filter(user=self.request.user)

class CompanyApplicationUpdateView(generics.UpdateAPIView):
    """Update an existing application (only if status allows)"""
    
    serializer_class = CompanyApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only allow updates for pending or requires_info applications
        return CompanyApplication.objects.filter(
            user=self.request.user,
            application_status__in=['pending', 'requires_info']
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.application_status
        
        response = super().update(request, *args, **kwargs)
        
        # If status changed, create history record
        if 'application_status' in request.data and request.data['application_status'] != old_status:
            ApplicationStatusHistory.objects.create(
                application=instance,
                old_status=old_status,
                new_status=request.data['application_status'],
                changed_by=request.user,
                change_reason='Status updated by user'
            )
        
        return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_application_document(request):
    """Upload documents for an application"""
    
    application_id = request.data.get('application_id')
    if not application_id:
        return Response({
            'error': 'Application ID is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        application = CompanyApplication.objects.get(
            id=application_id,
            user=request.user
        )
    except CompanyApplication.DoesNotExist:
        return Response({
            'error': 'Application not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Create document record
    document_data = request.data.copy()
    document_data['application'] = application.id
    
    serializer = ApplicationDocumentSerializer(data=document_data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Document uploaded successfully',
            'document': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_status_check(request, application_id):
    """Check the current status of an application"""
    
    try:
        application = CompanyApplication.objects.get(
            id=application_id,
            user=request.user
        )
    except CompanyApplication.DoesNotExist:
        return Response({
            'error': 'Application not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CompanyApplicationDetailSerializer(application)
    return Response({
        'application': serializer.data,
        'current_status': application.application_status,
        'can_edit': application.application_status in ['pending', 'requires_info']
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_application_summary(request):
    """Get summary of all user applications"""
    
    applications = CompanyApplication.objects.filter(user=request.user)
    
    summary = {
        'total_applications': applications.count(),
        'pending': applications.filter(application_status='pending').count(),
        'under_review': applications.filter(application_status='under_review').count(),
        'approved': applications.filter(application_status='approved').count(),
        'rejected': applications.filter(application_status='rejected').count(),
        'requires_info': applications.filter(application_status='requires_info').count(),
    }
    
    recent_applications = applications.order_by('-created_at')[:5]
    serializer = CompanyApplicationSerializer(recent_applications, many=True)
    
    return Response({
        'summary': summary,
        'recent_applications': serializer.data
    })
