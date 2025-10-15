from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class CreditRating(models.Model):
    """Credit Rating System"""
    
    RATING_CHOICES = [
        ('AAA', 'AAA - Excellent'),
        ('AA', 'AA - Very Good'), 
        ('A', 'A - Good'),
        ('BBB', 'BBB - Fair'),
        ('BB', 'BB - Marginal'),
        ('B', 'B - Poor'),
        ('B+', 'B+ - Poor Plus'),
        ('CCC', 'CCC - Very Poor'),
        ('CC', 'CC - Extremely Poor'),
        ('C', 'C - Default Imminent'),
        ('D', 'D - In Default'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_ratings')
    company_name = models.CharField(max_length=200)
    credit_rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    
    # Important Dates
    application_date = models.DateField()
    settlement_date = models.DateField()
    evaluation_date = models.DateField()
    expiration_date = models.DateField()
    
    # Status
    STATUS_CHOICES = [
        ('effectiveness', 'Effectiveness'),
        ('processing', 'Processing'),
        ('expiration', 'Expiration'),
        ('cancelled', 'Cancelled'),
    ]
    report_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    
    # Report Details
    submission_office = models.CharField(max_length=200, default='View the main building')
    report_file = models.FileField(upload_to='credit_reports/', null=True, blank=True)
    
    # Financial Information
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    assets_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    liabilities = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Rating Details
    rating_rationale = models.TextField(blank=True, null=True)
    key_strengths = models.TextField(blank=True, null=True)
    key_concerns = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Credit Rating'
        verbose_name_plural = 'Credit Ratings'
    
    def __str__(self):
        return f"{self.company_name} - {self.credit_rating}"
    
    @property
    def is_expired(self):
        return self.expiration_date < timezone.now().date()
    
    @property
    def days_until_expiration(self):
        if self.expiration_date:
            delta = self.expiration_date - timezone.now().date()
            return delta.days
        return None

class UserProfile(models.Model):
    """Extended user profile for dashboard"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Company Information
    primary_company_name = models.CharField(max_length=200, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Profile Settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    
    # Dashboard Preferences
    default_dashboard_view = models.CharField(
        max_length=20,
        choices=[
            ('overview', 'Overview'),
            ('reports', 'My Reports'),
            ('history', 'Application History'),
        ],
        default='overview'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

class DashboardActivity(models.Model):
    """Track user activities for dashboard analytics"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    ACTIVITY_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('view_dashboard', 'Viewed Dashboard'),
        ('view_report', 'Viewed Report'),
        ('download_report', 'Downloaded Report'),
        ('print_invoice', 'Printed Invoice'),
        ('update_profile', 'Updated Profile'),
        ('submit_application', 'Submitted Application'),
    ]
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Related objects (optional)
    related_credit_rating = models.ForeignKey(
        CreditRating, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Dashboard Activity'
        verbose_name_plural = 'Dashboard Activities'
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

class ReportAccess(models.Model):
    """Track report access and permissions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credit_rating = models.ForeignKey(CreditRating, on_delete=models.CASCADE)
    access_type = models.CharField(
        max_length=20,
        choices=[
            ('view', 'View Only'),
            ('download', 'Download Allowed'),
            ('print', 'Print Allowed'),
            ('share', 'Share Allowed'),
        ],
        default='view'
    )
    accessed_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'credit_rating']
        ordering = ['-accessed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.credit_rating.company_name} access"
