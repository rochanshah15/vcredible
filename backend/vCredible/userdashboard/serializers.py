from rest_framework import serializers
from .models import CreditRating, UserProfile, DashboardActivity, ReportAccess
from django.contrib.auth import get_user_model

User = get_user_model()

class CreditRatingSerializer(serializers.ModelSerializer):
    """Serializer for Credit Rating data"""
    
    is_expired = serializers.ReadOnlyField()
    days_until_expiration = serializers.ReadOnlyField()
    
    class Meta:
        model = CreditRating
        fields = [
            'id',
            'company_name',
            'credit_rating',
            'application_date',
            'settlement_date', 
            'evaluation_date',
            'expiration_date',
            'report_status',
            'submission_office',
            'report_file',
            'annual_revenue',
            'assets_value',
            'liabilities',
            'rating_rationale',
            'key_strengths',
            'key_concerns',
            'is_expired',
            'days_until_expiration',
            'created_at',
            'updated_at',
            'is_active',
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at',
            'is_expired',
            'days_until_expiration'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for User Profile"""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'primary_company_name',
            'job_title',
            'phone_number',
            'email_notifications',
            'sms_notifications',
            'marketing_emails',
            'default_dashboard_view',
            'user_email',
            'user_full_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_email', 'user_full_name']

class DashboardActivitySerializer(serializers.ModelSerializer):
    """Serializer for Dashboard Activity tracking"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    related_company = serializers.CharField(source='related_credit_rating.company_name', read_only=True)
    
    class Meta:
        model = DashboardActivity
        fields = [
            'id',
            'activity_type',
            'description',
            'user_name',
            'related_company',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp', 'user_name', 'related_company']

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    
    total_applications = serializers.IntegerField()
    active_reports = serializers.IntegerField()
    expired_reports = serializers.IntegerField()
    latest_credit_rating = serializers.CharField()
    pending_applications = serializers.IntegerField()
    approved_applications = serializers.IntegerField()

class DashboardOverviewSerializer(serializers.Serializer):
    """Serializer for complete dashboard overview"""
    
    stats = DashboardStatsSerializer()
    recent_credit_ratings = CreditRatingSerializer(many=True)
    recent_activities = DashboardActivitySerializer(many=True)
    profile = UserProfileSerializer()

class ReportAccessSerializer(serializers.ModelSerializer):
    """Serializer for Report Access tracking"""
    
    company_name = serializers.CharField(source='credit_rating.company_name', read_only=True)
    credit_rating_value = serializers.CharField(source='credit_rating.credit_rating', read_only=True)
    
    class Meta:
        model = ReportAccess
        fields = [
            'id',
            'access_type',
            'accessed_at',
            'expires_at',
            'is_active',
            'company_name',
            'credit_rating_value',
        ]
        read_only_fields = ['id', 'accessed_at', 'company_name', 'credit_rating_value']
