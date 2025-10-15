from django.contrib import admin
from .models import CompanyApplication, ApplicationDocument, ApplicationStatusHistory

@admin.register(CompanyApplication)
class CompanyApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'company_name', 
        'user', 
        'application_status', 
        'created_at',
        'reviewed_at'
    ]
    list_filter = [
        'application_status', 
        'business_type',
        'country',
        'created_at',
        'terms_accepted'
    ]
    search_fields = [
        'company_name', 
        'registration_number', 
        'email',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company Information', {
            'fields': (
                'user',
                'company_name',
                'business_type',
                'registration_number',
                'established_year',
            )
        }),
        ('Address', {
            'fields': (
                'address_line_1',
                'address_line_2',
                'city',
                'state',
                'postal_code',
                'country',
            )
        }),
        ('Contact Information', {
            'fields': (
                'phone_number',
                'email',
                'website',
            )
        }),
        ('Business Details', {
            'fields': (
                'selected_business_category',
                'business_subcategory',
                'annual_revenue',
                'employee_count',
                'business_verification_code',
            )
        }),
        ('Terms & Conditions', {
            'fields': (
                'terms_accepted',
                'privacy_policy_accepted',
                'marketing_consent',
            )
        }),
        ('Application Status', {
            'fields': (
                'application_status',
                'reviewed_by',
                'reviewed_at',
                'review_notes',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ['application', 'document_type', 'document_name', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['application__company_name', 'document_name']

@admin.register(ApplicationStatusHistory) 
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['old_status', 'new_status', 'changed_at']
    search_fields = ['application__company_name', 'changed_by__email']
    readonly_fields = ['changed_at']
