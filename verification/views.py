from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from certificates.models import Certificate
from .models import VerificationRequest, VerificationLog
from .serializers import (
    VerificationRequestSerializer, VerificationLogSerializer,
    CertificateVerifySerializer
)
from .utils import get_client_ip, get_user_agent

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_certificate(request):
    """Verify a certificate by ID"""
    serializer = CertificateVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    certificate_id = serializer.validated_data['certificate_id']
    
    try:
        certificate = Certificate.objects.get(certificate_id=certificate_id)
        
        # Create verification request
        verification_request = VerificationRequest.objects.create(
            certificate=certificate,
            requester_ip=get_client_ip(request),
            requester_user_agent=get_user_agent(request),
            requester_email=serializer.validated_data.get('requester_email', ''),
            requester_organization=serializer.validated_data.get('requester_organization', ''),
            verification_result=certificate.status == 'issued' and certificate.is_verified,
            verification_method='web'
        )
        
        # Create verification log
        VerificationLog.objects.create(
            certificate=certificate,
            user=request.user if request.user.is_authenticated else None,
            action='verify',
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                'certificate_id': certificate_id,
                'verification_request_id': str(verification_request.id)
            }
        )
        
        # Prepare response data
        if verification_request.verification_result:
            response_data = {
                'is_valid': True,
                'certificate': {
                    'id': certificate.certificate_id,
                    'title': certificate.title,
                    'holder_name': certificate.holder.full_name,
                    'holder_email': certificate.holder.email,
                    'institution_name': certificate.institution_name,
                    'institution_address': certificate.institution_address,
                    'degree': certificate.degree,
                    'field_of_study': certificate.field_of_study,
                    'grade': certificate.grade,
                    'issue_date': certificate.issue_date,
                    'expiry_date': certificate.expiry_date,
                    'status': certificate.status,
                    'blockchain_hash': certificate.blockchain_hash,
                    'qr_code': certificate.qr_code.url if certificate.qr_code else None,
                },
                'verification': {
                    'verification_date': verification_request.verification_date,
                    'verification_id': str(verification_request.id),
                }
            }
        else:
            response_data = {
                'is_valid': False,
                'message': 'Sertifikat topilmadi yoki haqiqiy emas',
                'certificate_id': certificate_id
            }
        
        return Response(response_data)
        
    except Certificate.DoesNotExist:
        # Create failed verification log
        VerificationLog.objects.create(
            certificate=None,
            user=request.user if request.user.is_authenticated else None,
            action='verify',
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={
                'certificate_id': certificate_id,
                'error': 'Certificate not found'
            }
        )
        
        return Response({
            'is_valid': False,
            'message': 'Sertifikat topilmadi',
            'certificate_id': certificate_id
        })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verification_history(request):
    """Get verification history for current user"""
    user = request.user
    
    if user.role == 'admin':
        # Admin can see all verifications
        verifications = VerificationRequest.objects.all()
    elif user.role == 'organization':
        # Organization can see verifications for their certificates
        verifications = VerificationRequest.objects.filter(certificate__issuer=user)
    else:
        # Students can see verifications for their certificates
        verifications = VerificationRequest.objects.filter(certificate__holder=user)
    
    # Apply pagination and filtering
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 20)
    
    # Filter by date range if provided
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    
    if date_from:
        verifications = verifications.filter(verification_date__gte=date_from)
    if date_to:
        verifications = verifications.filter(verification_date__lte=date_to)
    
    verifications = verifications.order_by('-verification_date')[:int(page_size)]
    
    serializer = VerificationRequestSerializer(verifications, many=True)
    return Response({
        'results': serializer.data,
        'count': verifications.count()
    })

class VerificationLogListView(generics.ListAPIView):
    serializer_class = VerificationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['action', 'certificate__status']
    search_fields = ['certificate__title', 'certificate__certificate_id']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            return VerificationLog.objects.all()
        elif user.role == 'organization':
            return VerificationLog.objects.filter(certificate__issuer=user)
        else:
            return VerificationLog.objects.filter(certificate__holder=user)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verification_stats(request):
    """Get verification statistics"""
    user = request.user
    
    if user.role == 'admin':
        total_verifications = VerificationRequest.objects.count()
        successful_verifications = VerificationRequest.objects.filter(verification_result=True).count()
    elif user.role == 'organization':
        total_verifications = VerificationRequest.objects.filter(certificate__issuer=user).count()
        successful_verifications = VerificationRequest.objects.filter(
            certificate__issuer=user, verification_result=True
        ).count()
    else:
        total_verifications = VerificationRequest.objects.filter(certificate__holder=user).count()
        successful_verifications = VerificationRequest.objects.filter(
            certificate__holder=user, verification_result=True
        ).count()
    
    failed_verifications = total_verifications - successful_verifications
    success_rate = (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0
    
    return Response({
        'total_verifications': total_verifications,
        'successful_verifications': successful_verifications,
        'failed_verifications': failed_verifications,
        'success_rate': round(success_rate, 2)
    })
