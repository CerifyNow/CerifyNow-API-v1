from django.urls import path
from .views import (
    verify_certificate, verify_by_qr, verification_history,
    VerificationLogListView, verification_stats
)

urlpatterns = [
    path('verify/', verify_certificate, name='verify-certificate'),
    path('verify-qr/<str:qr_hash>/', verify_by_qr, name='verify-by-qr'),
    path('history/', verification_history, name='verification-history'),
    path('logs/', VerificationLogListView.as_view(), name='verification-logs'),
    path('stats/', verification_stats, name='verification-stats'),
]
