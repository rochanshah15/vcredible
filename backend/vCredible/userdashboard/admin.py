from django.contrib import admin
from .models import CreditRating, UserProfile, DashboardActivity, ReportAccess

@admin.register(CreditRating)
class CreditRatingAdmin(admin.ModelAdmin):
    list_display = [
        'company_name',
        'user',
        'credit_rating',
        'report_status',
        'application_date',
        'expiration_date',
        'is_expired'
    ]
    list_filter = [
        'credit_rating',
        'report_status', 
        'application_date',
        'expiration_date',
        'is_active'
    ]
    search_fields = [
        'company_name',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'is_expired', 'days_until_expiration']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user',
                'company_name',
                'credit_rating',
                'report_status',
            )
        }),
        ('Dates', {
            'fields': (
                'application_date',
                'settlement_date',
                'evaluation_date',
                'expiration_date',
                'is_expired',
                'days_until_expiration',
            )
        }),
        ('Financial Information', {
            'fields': (
                'annual_revenue',
                'assets_value',
                'liabilities',
            )
        }),
        ('Rating Details', {
            'fields': (
                'rating_rationale',
                'key_strengths',
                'key_concerns',
                'submission_office',
                'report_file',
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'primary_company_name',
        'job_title',
        'email_notifications',
        'created_at'
    ]
    list_filter = [
        'email_notifications',
        'sms_notifications',
        'marketing_emails',
        'default_dashboard_view'
    ]
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'primary_company_name'
    ]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(DashboardActivity)
class DashboardActivityAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'activity_type',
        'description',
        'related_credit_rating',
        'timestamp'
    ]
    list_filter = [
        'activity_type',
        'timestamp'
    ]
    search_fields = [
        'user__email',
        'description',
        'related_credit_rating__company_name'
    ]
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'related_credit_rating')

@admin.register(ReportAccess)
class ReportAccessAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'credit_rating',
        'access_type',
        'accessed_at',
        'expires_at',
        'is_active'
    ]
    list_filter = [
        'access_type',
        'is_active',
        'accessed_at'
    ]
    search_fields = [
        'user__email',
        'credit_rating__company_name'
    ]
    readonly_fields = ['accessed_at']
