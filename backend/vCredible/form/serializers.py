from rest_framework import serializers
from .models import CompanyApplication, ApplicationDocument, ApplicationStatusHistory

class CompanyApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Company Application form data"""
    
    class Meta:
        model = CompanyApplication
        fields = [
            'id',
            # Step 1: Company Information
            'company_name',
            'business_type', 
            'registration_number',
            'established_year',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
            'phone_number',
            'email',
            'website',
            
            # Additional Contact Information from Form
            'person_in_charge',
            'personal_contact_number',
            'assignment_type',
            
            # Step 2: Business Search
            'selected_business_category',
            'business_subcategory',
            'annual_revenue',
            'employee_count',
            
            # Step 3: Business Code
            'business_verification_code',
            
            # Step 4: Terms
            'terms_accepted',
            'privacy_policy_accepted',
            'marketing_consent',
            
            # Status and metadata
            'application_status',
            'created_at',
            'updated_at',
            'review_notes',
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'user', 
            'reviewed_by', 
            'reviewed_at'
        ]
    
    def create(self, validated_data):
        # Add the current user to the application
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms and conditions.")
        return value
    
    def validate_privacy_policy_accepted(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the privacy policy.")
        return value

class ApplicationDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Application Documents"""
    
    class Meta:
        model = ApplicationDocument
        fields = [
            'id',
            'application',
            'document_type',
            'document_name',
            'document_file',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at']

class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for Application Status History"""
    
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ApplicationStatusHistory
        fields = [
            'id',
            'application',
            'old_status',
            'new_status',
            'changed_by',
            'changed_by_name',
            'change_reason',
            'changed_at',
        ]
        read_only_fields = ['id', 'changed_at', 'changed_by', 'changed_by_name']

class CompanyApplicationDetailSerializer(CompanyApplicationSerializer):
    """Detailed serializer with related data"""
    
    documents = ApplicationDocumentSerializer(many=True, read_only=True)
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta(CompanyApplicationSerializer.Meta):
        fields = CompanyApplicationSerializer.Meta.fields + [
            'documents',
            'status_history', 
            'user_name',
            'user_email'
        ]
