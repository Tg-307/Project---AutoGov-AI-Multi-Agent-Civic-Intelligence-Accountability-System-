from django.urls import path
from .views import (
    UploadIssueView, SendComplaintView, IssueListView, IssueDetailView,
    ResolveIssueView, EscalateView, RatingsView, DashboardView,
)

urlpatterns = [
    path('upload/', UploadIssueView.as_view(), name='upload'),
    path('issues/', IssueListView.as_view(), name='issue-list'),
    path('issues/<int:issue_id>/', IssueDetailView.as_view(), name='issue-detail'),
    path('send/<int:issue_id>/', SendComplaintView.as_view(), name='send-complaint'),
    path('resolve/<int:issue_id>/', ResolveIssueView.as_view(), name='resolve-issue'),
    path('escalate/', EscalateView.as_view(), name='escalate'),
    path('ratings/', RatingsView.as_view(), name='ratings'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
