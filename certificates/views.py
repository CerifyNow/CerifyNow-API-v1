from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from certificates.models import Certificate, CertificateTemplate, CertificateVerification
from certificates.serializers import (
    CertificateSerializer, CertificateCreateSerializer,
    CertificateTemplateSerializer, CertificateVerificationSerializer,
    CertificateStatsSerializer
)
from certificates.permissions import (
    CanCreateCertificatePermission, IsOwnerOrIssuerOrCanView,
    IsSuperAdminPermission, IsInstitutionAdminPermission
)


@extend_schema(
    summary="List and Create Certificates",
    description="List all certificates for the current user based on their role or create a new certificate (issuer only).",
    request=CertificateCreateSerializer,
    responses={
        200: OpenApiResponse(response=CertificateSerializer, description="List of certificates"),
        201: OpenApiResponse(response=CertificateSerializer, description="Certificate successfully created"),
        400: OpenApiResponse(description="Invalid input data"),
        403: OpenApiResponse(description="Permission denied"),
    },
    tags=["Certificates"]
)
class CertificateListCreateView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'certificate_type', 'is_verified']
    search_fields = ['title', 'certificate_id', 'holder__first_name', 'holder__last_name']
    ordering_fields = ['created_at', 'issue_date', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Certificate.objects.all()
        elif user.role == 'admin':
            return Certificate.objects.filter(issuer=user)
        elif user.role == 'student':
            return Certificate.objects.filter(holder=user)
        elif user.role == 'checker':
            # Checker can view all certificates for verification purposes
            return Certificate.objects.all()
        return Certificate.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CertificateCreateSerializer
        return CertificateSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [CanCreateCertificatePermission()]
        return [permissions.IsAuthenticated()]


@extend_schema(
        summary="Retrieve, Update or Delete a Certificate",
        description="Retrieve certificate details, or update/delete them if you have the proper permissions.",
        responses={
            200: OpenApiResponse(response=CertificateSerializer, description="Certificate details"),
            204: OpenApiResponse(description="Certificate deleted successfully"),
            400: OpenApiResponse(description="Invalid data"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Certificate not found"),
        },
        request=CertificateSerializer,
        tags=["Certificates"]
    )

class CertificateDetailView(generics.RetrieveUpdateDestroyAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsOwnerOrIssuerOrCanView]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only superadmin and issuer can modify
            return [permissions.IsAuthenticated()]
        return [IsOwnerOrIssuerOrCanView()]

    def perform_update(self, serializer):
        # Only allow updates by superadmin or issuer
        if self.request.user.role == 'superadmin' or serializer.instance.issuer == self.request.user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("Siz bu sertifikatni o'zgartira olmaysiz")

    def perform_destroy(self, instance):
        # Only superadmin can delete
        if self.request.user.role != 'superadmin':
            raise permissions.PermissionDenied("Faqat superadmin sertifikatni o'chira oladi")
        instance.delete()

@extend_schema(
    summary="Get Certificate Stats",
    description="Return total, verified, pending, revoked certificates and verification counts based on user role.",
    responses={
        200: OpenApiResponse(response=CertificateStatsSerializer, description="Certificate statistics"),
        403: OpenApiResponse(description="Permission denied")
    },
    tags=["Certificates"]
)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def certificate_stats(request):
    """Get certificate statistics for dashboard"""
    user = request.user

    if user.role == 'superadmin':
        queryset = Certificate.objects.all()
    elif user.role == 'admin':
        queryset = Certificate.objects.filter(issuer=user)
    elif user.role == 'student':
        queryset = Certificate.objects.filter(holder=user)
    elif user.role == 'checker':
        queryset = Certificate.objects.all()
    else:
        queryset = Certificate.objects.none()

    # Calculate stats
    total_certificates = queryset.count()
    verified_certificates = queryset.filter(is_verified=True).count()
    pending_certificates = queryset.filter(status='draft').count()
    revoked_certificates = queryset.filter(status='revoked').count()

    # This month certificates
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    certificates_this_month = queryset.filter(created_at__gte=this_month).count()

    # Verification count based on role
    if user.role == 'superadmin':
        verifications_count = CertificateVerification.objects.count()
    elif user.role == 'admin':
        verifications_count = CertificateVerification.objects.filter(
            certificate__issuer=user
        ).count()
    elif user.role == 'student':
        verifications_count = CertificateVerification.objects.filter(
            certificate__holder=user
        ).count()
    elif user.role == 'checker':
        verifications_count = CertificateVerification.objects.count()
    else:
        verifications_count = 0

    stats = {
        'total_certificates': total_certificates,
        'verified_certificates': verified_certificates,
        'pending_certificates': pending_certificates,
        'revoked_certificates': revoked_certificates,
        'certificates_this_month': certificates_this_month,
        'verifications_count': verifications_count,
    }

    serializer = CertificateStatsSerializer(stats)
    return Response(serializer.data)


@extend_schema(
    summary="Bulk Create Certificates",
    description="Create multiple certificates in one request. Only institution admins can perform this.",
    request=CertificateCreateSerializer(many=True),
    responses={
        200: OpenApiResponse(description="Certificates created with details and errors if any"),
        403: OpenApiResponse(description="Permission denied")
    },
    tags=["Certificates"]
)

@api_view(['POST'])
@permission_classes([IsInstitutionAdminPermission])
def bulk_create_certificates(request):
    """Bulk create certificates - only for institution admins"""
    certificates_data = request.data.get('certificates', [])
    created_certificates = []
    errors = []

    for i, cert_data in enumerate(certificates_data):
        serializer = CertificateCreateSerializer(
            data=cert_data,
            context={'request': request}
        )

        if serializer.is_valid():
            certificate = serializer.save()
            created_certificates.append(CertificateSerializer(certificate).data)
        else:
            errors.append({
                'row': i + 1,
                'errors': serializer.errors
            })

    return Response({
        'created_count': len(created_certificates),
        'error_count': len(errors),
        'created_certificates': created_certificates,
        'errors': errors
    })


@extend_schema(
    summary="Revoke a Certificate",
    description="Revoke a certificate (set as 'revoked' and not verified). Only superadmin can revoke.",
    responses={
        200: OpenApiResponse(response=CertificateSerializer, description="Certificate revoked"),
        404: OpenApiResponse(description="Certificate not found"),
        403: OpenApiResponse(description="Permission denied")
    },
    tags=["Certificates"]
)

@api_view(['POST'])
@permission_classes([IsSuperAdminPermission])
def revoke_certificate(request, pk):
    """Revoke a certificate - only superadmin"""
    try:
        certificate = Certificate.objects.get(pk=pk)
        certificate.status = 'revoked'
        certificate.is_verified = False
        certificate.save()

        return Response({
            'message': 'Sertifikat bekor qilindi',
            'certificate': CertificateSerializer(certificate).data
        })
    except Certificate.DoesNotExist:
        return Response(
            {'error': 'Sertifikat topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )
