from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()

class CompanyApplication(models.Model):
    """Model to store company registration applications from the multi-step form"""
    
    # Step 1: Company Information
    company_name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    established_year = models.IntegerField()
    
    # Address Information
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    
    # Contact Information
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_validator], max_length=17)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    
    # Additional Contact Information from Form
    person_in_charge = models.CharField(max_length=200, blank=True, null=True)
    personal_contact_number = models.CharField(max_length=17, blank=True, null=True)
    assignment_type = models.CharField(
        max_length=20,
        choices=[
            ('Purchase', 'Purchase'),
            ('Sale', 'Sale'),
            ('Both', 'Both'),
        ],
        default='Purchase'
    )
    
    # Step 2: Business Search (selected business details)
    selected_business_category = models.CharField(max_length=100)
    business_subcategory = models.CharField(max_length=100, blank=True, null=True)
    annual_revenue = models.CharField(max_length=50, blank=True, null=True)
    employee_count = models.CharField(max_length=50, blank=True, null=True)
    
    # Step 3: Business Code
    business_verification_code = models.CharField(max_length=100)
    
    # Step 4: Terms and Conditions
    terms_accepted = models.BooleanField(default=False)
    privacy_policy_accepted = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)
    
    # Application Metadata
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    application_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Review'),
            ('under_review', 'Under Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('requires_info', 'Requires Additional Information'),
        ],
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval/Review fields
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_applications'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Company Application'
        verbose_name_plural = 'Company Applications'
    
    def __str__(self):
        return f"{self.company_name} - {self.application_status}"

class ApplicationDocument(models.Model):
    """Model to store documents uploaded with applications"""
    
    application = models.ForeignKey(
        CompanyApplication, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=50,
        choices=[
            ('business_license', 'Business License'),
            ('tax_certificate', 'Tax Certificate'),
            ('incorporation_cert', 'Certificate of Incorporation'),
            ('financial_statement', 'Financial Statement'),
            ('other', 'Other Document'),
        ]
    )
    document_name = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='application_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.application.company_name} - {self.document_type}"

class ApplicationStatusHistory(models.Model):
    """Track status changes for applications"""
    
    application = models.ForeignKey(
        CompanyApplication,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_reason = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = 'Application Status History'
        verbose_name_plural = 'Application Status Histories'
    
    def __str__(self):
        return f"{self.application.company_name}: {self.old_status} → {self.new_status}"
