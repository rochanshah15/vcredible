from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import CreditRating, UserProfile, DashboardActivity, ReportAccess
from .serializers import (
    CreditRatingSerializer,
    UserProfileSerializer, 
    DashboardActivitySerializer,
    DashboardStatsSerializer,
    DashboardOverviewSerializer,
    ReportAccessSerializer
)
from form.models import CompanyApplication

class DashboardOverviewView(generics.GenericAPIView):
    """Complete dashboard overview with stats, reports, and activities"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Calculate statistics
        applications = CompanyApplication.objects.filter(user=user)
        credit_ratings = CreditRating.objects.filter(user=user, is_active=True)
        
        stats = {
            'total_applications': applications.count(),
            'active_reports': credit_ratings.filter(
                report_status='effectiveness',
                expiration_date__gte=timezone.now().date()
            ).count(),
            'expired_reports': credit_ratings.filter(
                Q(expiration_date__lt=timezone.now().date()) | 
                Q(report_status='expiration')
            ).count(),
            'latest_credit_rating': credit_ratings.order_by('-created_at').first().credit_rating if credit_ratings.exists() else 'N/A',
            'pending_applications': applications.filter(application_status='pending').count(),
            'approved_applications': applications.filter(application_status='approved').count(),
        }
        
        # Get recent credit ratings
        recent_credit_ratings = credit_ratings.order_by('-created_at')[:5]
        
        # Get recent activities
        recent_activities = DashboardActivity.objects.filter(user=user).order_by('-timestamp')[:10]
        
        # Log this dashboard view
        DashboardActivity.objects.create(
            user=user,
            activity_type='view_dashboard',
            description='Viewed dashboard overview',
            ip_address=self.get_client_ip(request)
        )
        
        # Serialize data
        stats_serializer = DashboardStatsSerializer(stats)
        credit_ratings_serializer = CreditRatingSerializer(recent_credit_ratings, many=True)
        activities_serializer = DashboardActivitySerializer(recent_activities, many=True)
        profile_serializer = UserProfileSerializer(profile)
        
        return Response({
            'stats': stats_serializer.data,
            'recent_credit_ratings': credit_ratings_serializer.data,
            'recent_activities': activities_serializer.data,
            'profile': profile_serializer.data,
            'user': {
                'name': user.get_full_name(),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class CreditRatingListView(generics.ListAPIView):
    """List all credit ratings for the current user"""
    
    serializer_class = CreditRatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CreditRating.objects.filter(user=self.request.user, is_active=True)

class CreditRatingDetailView(generics.RetrieveAPIView):
    """Get detailed view of a specific credit rating"""
    
    serializer_class = CreditRatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CreditRating.objects.filter(user=self.request.user, is_active=True)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Log report view activity
        DashboardActivity.objects.create(
            user=request.user,
            activity_type='view_report',
            description=f'Viewed credit rating report for {instance.company_name}',
            related_credit_rating=instance,
            ip_address=self.get_client_ip(request)
        )
        
        # Create or update report access
        ReportAccess.objects.update_or_create(
            user=request.user,
            credit_rating=instance,
            defaults={
                'access_type': 'view',
                'is_active': True
            }
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        # Log profile update activity
        DashboardActivity.objects.create(
            user=request.user,
            activity_type='update_profile',
            description='Updated profile information'
        )
        
        return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_reports(request):
    """Get all active (non-expired) reports"""
    
    credit_ratings = CreditRating.objects.filter(
        user=request.user,
        is_active=True,
        report_status='effectiveness',
        expiration_date__gte=timezone.now().date()
    )
    
    serializer = CreditRatingSerializer(credit_ratings, many=True)
    return Response({
        'active_reports': serializer.data,
        'count': credit_ratings.count()
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def application_history(request):
    """Get complete application history"""
    
    credit_ratings = CreditRating.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-created_at')
    
    serializer = CreditRatingSerializer(credit_ratings, many=True)
    return Response({
        'history': serializer.data,
        'total_count': credit_ratings.count()
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def print_invoice(request):
    """Log print invoice activity"""
    
    rating_id = request.data.get('rating_id')
    
    try:
        if rating_id:
            credit_rating = CreditRating.objects.get(
                id=rating_id,
                user=request.user
            )
            
            # Log print activity
            DashboardActivity.objects.create(
                user=request.user,
                activity_type='print_invoice',
                description=f'Printed invoice for {credit_rating.company_name}',
                related_credit_rating=credit_rating
            )
            
            # Update report access
            ReportAccess.objects.update_or_create(
                user=request.user,
                credit_rating=credit_rating,
                defaults={
                    'access_type': 'print',
                    'is_active': True
                }
            )
            
            return Response({
                'message': 'Print request logged successfully',
                'company_name': credit_rating.company_name
            })
        else:
            # Generic print activity
            DashboardActivity.objects.create(
                user=request.user,
                activity_type='print_invoice',
                description='Printed invoice'
            )
            
            return Response({
                'message': 'Print request logged successfully'
            })
            
    except CreditRating.DoesNotExist:
        return Response({
            'error': 'Credit rating not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST']) 
@permission_classes([IsAuthenticated])
def download_report(request):
    """Log download report activity"""
    
    rating_id = request.data.get('rating_id')
    
    try:
        credit_rating = CreditRating.objects.get(
            id=rating_id,
            user=request.user
        )
        
        # Log download activity
        DashboardActivity.objects.create(
            user=request.user,
            activity_type='download_report',
            description=f'Downloaded report for {credit_rating.company_name}',
            related_credit_rating=credit_rating
        )
        
        # Update report access
        ReportAccess.objects.update_or_create(
            user=request.user,
            credit_rating=credit_rating,
            defaults={
                'access_type': 'download',
                'is_active': True
            }
        )
        
        return Response({
            'message': 'Download logged successfully',
            'report_url': credit_rating.report_file.url if credit_rating.report_file else None,
            'company_name': credit_rating.company_name
        })
        
    except CreditRating.DoesNotExist:
        return Response({
            'error': 'Credit rating not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_activities(request):
    """Get user's recent activities"""
    
    activities = DashboardActivity.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:20]
    
    serializer = DashboardActivitySerializer(activities, many=True)
    return Response({
        'activities': serializer.data,
        'count': activities.count()
    })
