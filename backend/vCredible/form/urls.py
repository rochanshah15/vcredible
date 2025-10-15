from django.urls import path
from . import views

app_name = 'form'

urlpatterns = [
    # Company Application URLs
    path('applications/', views.CompanyApplicationListView.as_view(), name='application-list'),
    path('applications/create/', views.CompanyApplicationCreateView.as_view(), name='application-create'),
    path('applications/<int:pk>/', views.CompanyApplicationDetailView.as_view(), name='application-detail'),
    path('applications/<int:pk>/update/', views.CompanyApplicationUpdateView.as_view(), name='application-update'),
    
    # Document Upload
    path('applications/documents/upload/', views.upload_application_document, name='document-upload'),
    
    # Status and Summary
    path('applications/<int:application_id>/status/', views.application_status_check, name='application-status'),
    path('applications/summary/', views.user_application_summary, name='application-summary'),
]
