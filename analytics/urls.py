from django.urls import path
from .views import (
    dashboard_analytics, analytics_overview, certificate_analytics,
    verification_analytics, SystemStatsListView
)

urlpatterns = [
    path('dashboard/', dashboard_analytics, name='dashboard-analytics'),
    path('overview/', analytics_overview, name='analytics-overview'),
    path('certificates/', certificate_analytics, name='certificate-analytics'),
    path('verifications/', verification_analytics, name='verification-analytics'),
    path('system-stats/', SystemStatsListView.as_view(), name='system-stats'),
]
