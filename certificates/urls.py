from django.urls import path
from .views import (
    CertificateListCreateView, CertificateDetailView,
    CertificateTemplateListCreateView, CertificateTemplateDetailView,
    certificate_stats, bulk_create_certificates, revoke_certificate
)

urlpatterns = [
    path('', CertificateListCreateView.as_view(), name='certificate-list-create'),
    path('<uuid:pk>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('<uuid:pk>/revoke/', revoke_certificate, name='certificate-revoke'),
    path('bulk-create/', bulk_create_certificates, name='certificate-bulk-create'),
    path('stats/', certificate_stats, name='certificate-stats'),
    
    # Templates
    path('templates/', CertificateTemplateListCreateView.as_view(), name='template-list-create'),
    path('templates/<int:pk>/', CertificateTemplateDetailView.as_view(), name='template-detail'),
]
