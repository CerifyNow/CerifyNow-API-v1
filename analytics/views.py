from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from certificates.models import Certificate
from verification.models import VerificationRequest
from .models import SystemStats
from .serializers import SystemStatsSerializer, AnalyticsOverviewSerializer


User = get_user_model()

@extend_schema(
    summary="Dashboard Analytics",
    description="Hozirgi foydalanuvchining roli asosida statistik ma'lumotlarni qaytaradi (admin, organization yoki student).",
    responses={
        200: OpenApiResponse(description="Statistik ma'lumotlar muvaffaqiyatli qaytarildi"),
        401: OpenApiResponse(description="Avtorizatsiya talab qilinadi")
    },
    tags=["Analytics"]
)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_analytics(request):
    """Get dashboard analytics for current user"""
    user = request.user
    
    # Calculate stats based on user role
    if user.role == 'admin':
        # Admin sees system-wide stats
        total_certificates = Certificate.objects.count()
        verified_certificates = Certificate.objects.filter(is_verified=True).count()
        pending_certificates = Certificate.objects.filter(status='draft').count()
        revoked_certificates = Certificate.objects.filter(status='revoked').count()
        
        total_verifications = VerificationRequest.objects.count()
        successful_verifications = VerificationRequest.objects.filter(verification_result=True).count()
        
    elif user.role == 'organization':
        # Organization sees their issued certificates
        total_certificates = Certificate.objects.filter(issuer=user).count()
        verified_certificates = Certificate.objects.filter(issuer=user, is_verified=True).count()
        pending_certificates = Certificate.objects.filter(issuer=user, status='draft').count()
        revoked_certificates = Certificate.objects.filter(issuer=user, status='revoked').count()
        
        total_verifications = VerificationRequest.objects.filter(certificate__issuer=user).count()
        successful_verifications = VerificationRequest.objects.filter(
            certificate__issuer=user, verification_result=True
        ).count()
        
    else:  # student
        # Student sees their certificates
        total_certificates = Certificate.objects.filter(holder=user).count()
        verified_certificates = Certificate.objects.filter(holder=user, is_verified=True).count()
        pending_certificates = Certificate.objects.filter(holder=user, status='draft').count()
        revoked_certificates = Certificate.objects.filter(holder=user, status='revoked').count()
        
        total_verifications = VerificationRequest.objects.filter(certificate__holder=user).count()
        successful_verifications = VerificationRequest.objects.filter(
            certificate__holder=user, verification_result=True
        ).count()
    
    # Calculate monthly stats
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    if user.role == 'admin':
        certificates_this_month = Certificate.objects.filter(created_at__gte=this_month).count()
        verifications_this_month = VerificationRequest.objects.filter(verification_date__gte=this_month).count()
    elif user.role == 'organization':
        certificates_this_month = Certificate.objects.filter(issuer=user, created_at__gte=this_month).count()
        verifications_this_month = VerificationRequest.objects.filter(
            certificate__issuer=user, verification_date__gte=this_month
        ).count()
    else:
        certificates_this_month = Certificate.objects.filter(holder=user, created_at__gte=this_month).count()
        verifications_this_month = VerificationRequest.objects.filter(
            certificate__holder=user, verification_date__gte=this_month
        ).count()
    
    # Calculate success rate
    success_rate = (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0
    
    data = {
        'total_certificates': total_certificates,
        'verified_certificates': verified_certificates,
        'pending_certificates': pending_certificates,
        'revoked_certificates': revoked_certificates,
        'certificates_this_month': certificates_this_month,
        'total_verifications': total_verifications,
        'successful_verifications': successful_verifications,
        'verifications_this_month': verifications_this_month,
        'success_rate': round(success_rate, 2)
    }
    
    return Response(data)


@extend_schema(
    summary="Analytics Overview (Admin only)",
    description="Tizimdagi umumiy statistika: foydalanuvchilar, sertifikatlar, verifikatsiyalar, o'sish ko'rsatkichlari va boshqalar (faqat adminlar uchun).",
    responses={
        200: OpenApiResponse(description="Barcha statistik ma'lumotlar muvaffaqiyatli qaytarildi"),
        403: OpenApiResponse(description="Faqat administratorlar ko'rishi mumkin")
    },
    tags=["Analytics"]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def analytics_overview(request):
    """Get comprehensive analytics overview (Admin only)"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Faqat administratorlar bu ma\'lumotni ko\'ra oladi'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # User analytics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    students_count = User.objects.filter(role='student').count()
    organizations_count = User.objects.filter(role='organization').count()
    admins_count = User.objects.filter(role='admin').count()
    
    # Certificate analytics
    total_certificates = Certificate.objects.count()
    verified_certificates = Certificate.objects.filter(is_verified=True).count()
    pending_certificates = Certificate.objects.filter(status='draft').count()
    
    # Monthly certificates
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    certificates_this_month = Certificate.objects.filter(created_at__gte=this_month).count()
    
    # Verification analytics
    total_verifications = VerificationRequest.objects.count()
    successful_verifications = VerificationRequest.objects.filter(verification_result=True).count()
    verification_success_rate = (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0
    verifications_this_month = VerificationRequest.objects.filter(verification_date__gte=this_month).count()
    
    # Growth analytics (compared to last month)
    last_month = this_month - timedelta(days=30)
    users_last_month = User.objects.filter(date_joined__lt=this_month, date_joined__gte=last_month).count()
    certificates_last_month = Certificate.objects.filter(created_at__lt=this_month, created_at__gte=last_month).count()
    
    user_growth_rate = ((total_users - users_last_month) / users_last_month * 100) if users_last_month > 0 else 0
    certificate_growth_rate = ((certificates_this_month - certificates_last_month) / certificates_last_month * 100) if certificates_last_month > 0 else 0
    
    data = {
        'total_users': total_users,
        'active_users': active_users,
        'students_count': students_count,
        'organizations_count': organizations_count,
        'admins_count': admins_count,
        'total_certificates': total_certificates,
        'verified_certificates': verified_certificates,
        'pending_certificates': pending_certificates,
        'certificates_this_month': certificates_this_month,
        'total_verifications': total_verifications,
        'successful_verifications': successful_verifications,
        'verification_success_rate': round(verification_success_rate, 2),
        'verifications_this_month': verifications_this_month,
        'user_growth_rate': round(user_growth_rate, 2),
        'certificate_growth_rate': round(certificate_growth_rate, 2),
    }
    
    serializer = AnalyticsOverviewSerializer(data)
    return Response(serializer.data)

@extend_schema(
    summary="Certificate Analytics",
    description="Foydalanuvchining (admin, tashkilot yoki student) sertifikatlari bo'yicha statistik tahlil.",
    responses={
        200: OpenApiResponse(description="Sertifikatlar statistikasi muvaffaqiyatli qaytarildi")
    },
    tags=["Analytics"]
)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def certificate_analytics(request):
    """Get detailed certificate analytics"""
    user = request.user
    
    # Base queryset based on user role
    if user.role == 'admin':
        certificates = Certificate.objects.all()
    elif user.role == 'organization':
        certificates = Certificate.objects.filter(issuer=user)
    else:
        certificates = Certificate.objects.filter(holder=user)
    
    # Certificate type distribution
    type_distribution = certificates.values('certificate_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Status distribution
    status_distribution = certificates.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Monthly certificate creation trend (last 12 months)
    monthly_trend = []
    for i in range(12):
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        count = certificates.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        monthly_trend.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    
    monthly_trend.reverse()
    
    # Top institutions (for admin)
    top_institutions = []
    if user.role == 'admin':
        top_institutions = certificates.values('institution_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
    
    return Response({
        'type_distribution': type_distribution,
        'status_distribution': status_distribution,
        'monthly_trend': monthly_trend,
        'top_institutions': top_institutions,
    })

@extend_schema(
    summary="Verification Analytics",
    description="Verifikatsiyalar bo'yicha kundalik trend, usullar va geografik statistikalar.",
    responses={
        200: OpenApiResponse(description="Verifikatsiya statistikasi muvaffaqiyatli qaytarildi")
    },
    tags=["Analytics"]
)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verification_analytics(request):
    """Get detailed verification analytics"""
    user = request.user
    
    # Base queryset based on user role
    if user.role == 'admin':
        verifications = VerificationRequest.objects.all()
    elif user.role == 'organization':
        verifications = VerificationRequest.objects.filter(certificate__issuer=user)
    else:
        verifications = VerificationRequest.objects.filter(certificate__holder=user)
    
    # Daily verification trend (last 30 days)
    daily_trend = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        count = verifications.filter(verification_date__date=date).count()
        successful_count = verifications.filter(
            verification_date__date=date,
            verification_result=True
        ).count()
        
        daily_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'total': count,
            'successful': successful_count,
            'failed': count - successful_count
        })
    
    daily_trend.reverse()
    
    # Verification method distribution
    method_distribution = verifications.values('verification_method').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Geographic distribution (by IP location - mock data)
    geographic_distribution = [
        {'country': 'O\'zbekiston', 'count': verifications.count() * 0.8},
        {'country': 'Qozog\'iston', 'count': verifications.count() * 0.1},
        {'country': 'Rossiya', 'count': verifications.count() * 0.05},
        {'country': 'Boshqalar', 'count': verifications.count() * 0.05},
    ]
    
    return Response({
        'daily_trend': daily_trend,
        'method_distribution': method_distribution,
        'geographic_distribution': geographic_distribution,
    })

@extend_schema(
    summary="System Stats (Admin only)",
    description="Tizimning kunlik statistikasi (faqat administratorlar uchun). So'nggi 30 kunlik yozuvlar qaytariladi.",
    responses={
        200: OpenApiResponse(description="System statistikasi muvaffaqiyatli qaytarildi"),
        403: OpenApiResponse(description="Faqat administratorlar ko'rishi mumkin")
    },
    tags=["Analytics"]
)

class SystemStatsListView(generics.ListAPIView):
    queryset = SystemStats.objects.all()
    serializer_class = SystemStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role != 'admin':
            return SystemStats.objects.none()
        return SystemStats.objects.all()[:30]  # Last 30 days
