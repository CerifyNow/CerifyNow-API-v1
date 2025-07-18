from django.urls import path
from certificates.views import (
    CertificateListCreateView, CertificateDetailView,
    certificate_stats, bulk_create_certificates, revoke_certificate
)

urlpatterns = [
    path('', CertificateListCreateView.as_view(), name='certificate-list-create'),
    path('<uuid:pk>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('<uuid:pk>/revoke/', revoke_certificate, name='certificate-revoke'),
    path('bulk-create/', bulk_create_certificates, name='certificate-bulk-create'),
    path('stats/', certificate_stats, name='certificate-stats'),
]
