from django.urls import path
from .views import (
    verify_certificate, verification_history,
    VerificationLogListView, verification_stats
)

urlpatterns = [
    path('verify/', verify_certificate, name='verify-certificate'),
    path('history/', verification_history, name='verification-history'),
    path('logs/', VerificationLogListView.as_view(), name='verification-logs'),
    path('stats/', verification_stats, name='verification-stats'),
]
