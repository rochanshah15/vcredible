from django.urls import path
from . import views

app_name = 'userdashboard'

urlpatterns = [
    # Dashboard Overview
    path('overview/', views.DashboardOverviewView.as_view(), name='dashboard-overview'),
    
    # Credit Ratings
    path('credit-ratings/', views.CreditRatingListView.as_view(), name='credit-rating-list'),
    path('credit-ratings/<int:pk>/', views.CreditRatingDetailView.as_view(), name='credit-rating-detail'),
    
    # Reports
    path('reports/active/', views.active_reports, name='active-reports'),
    path('reports/history/', views.application_history, name='application-history'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Actions
    path('actions/print-invoice/', views.print_invoice, name='print-invoice'),
    path('actions/download-report/', views.download_report, name='download-report'),
    
    # Activities
    path('activities/', views.user_activities, name='user-activities'),
]
