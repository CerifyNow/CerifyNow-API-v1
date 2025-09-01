
from rest_framework import generics, permissions, status
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Certificate, CertificateVerification
from .serializers import CertificateSerializer
from .permissions import (
    CanCreateCertificatePermission,
    IsOwnerOrIssuerOrCanView,
)


class IsInstitutionAdminOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]


class CertificateListCreateView(generics.ListCreateAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanCreateCertificatePermission()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Certificate.objects.all()
        elif user.role == 'admin':
            return Certificate.objects.filter(institution_name=user.institution_name)
        elif user.role == 'student':
            return Certificate.objects.filter(holder_email=user.email)
        elif user.role == 'checker':
            return Certificate.objects.filter(is_verified=True)
        return Certificate.objects.none()


class CertificateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrIssuerOrCanView]

    def perform_update(self, serializer):
        user = self.request.user
        certificate = self.get_object()
        if user.role == 'superadmin':
            serializer.save()
        elif user.role == 'admin' and certificate.issuer == user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You do not have permission to update this certificate.")

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role == 'superadmin':
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this certificate.")


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def certificate_stats(request):
    user = request.user
    qs = Certificate.objects.all()

    if user.role == 'superadmin':
        pass
    elif user.role == 'admin':
        qs = qs.filter(institution_name=user.institution_name)
    elif user.role == 'student':
        qs = qs.filter(holder_email=user.email)
    elif user.role == 'checker':
        qs = qs.filter(is_verified=True)
    else:
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    stats = qs.aggregate(
        total=Count('id'),
        verified=Count('id', filter=qs.filter(is_verified=True)),
        revoked=Count('id', filter=qs.filter(is_revoked=True)),
    )
    return Response(stats)


@api_view(['POST'])
@permission_classes([IsInstitutionAdminOrSuperAdmin])
def bulk_create_certificates(request):
    serializer = CertificateSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save(issuer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_certificate(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    user = request.user

    if user.role in ['superadmin', 'admin'] and (user.role == 'superadmin' or certificate.issuer == user):
        certificate.is_revoked = True
        certificate.save()
        return Response({"status": "certificate revoked"}, status=status.HTTP_200_OK)

    return Response({"detail": "You do not have permission to revoke this certificate."},
                    status=status.HTTP_403_FORBIDDEN)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Certificate, CertificateVerification
from .serializers import CertificateSerializer
from .permissions import (
    CanCreateCertificatePermission,
    IsOwnerOrIssuerOrCanView,
)


class IsInstitutionAdminOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]


class CertificateListCreateView(generics.ListCreateAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanCreateCertificatePermission()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Certificate.objects.all()
        elif user.role == 'admin':
            return Certificate.objects.filter(institution_name=user.institution_name)
        elif user.role == 'student':
            return Certificate.objects.filter(holder_email=user.email)
        elif user.role == 'checker':
            return Certificate.objects.filter(is_verified=True)
        return Certificate.objects.none()


class CertificateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrIssuerOrCanView]

    def perform_update(self, serializer):
        user = self.request.user
        certificate = self.get_object()
        if user.role == 'superadmin':
            serializer.save()
        elif user.role == 'admin' and certificate.issuer == user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You do not have permission to update this certificate.")

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role == 'superadmin':
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this certificate.")


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def certificate_stats(request):
    user = request.user
    qs = Certificate.objects.all()

    if user.role == 'superadmin':
        pass
    elif user.role == 'admin':
        qs = qs.filter(institution_name=user.institution_name)
    elif user.role == 'student':
        qs = qs.filter(holder_email=user.email)
    elif user.role == 'checker':
        qs = qs.filter(is_verified=True)
    else:
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    stats = qs.aggregate(
        total=Count('id'),
        verified=Count('id', filter=qs.filter(is_verified=True)),
        revoked=Count('id', filter=qs.filter(is_revoked=True)),
    )
    return Response(stats)


@api_view(['POST'])
@permission_classes([IsInstitutionAdminOrSuperAdmin])
def bulk_create_certificates(request):
    serializer = CertificateSerializer(data=request.data, many=True)
    if serializer.is_valid():
        serializer.save(issuer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_certificate(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    user = request.user

    if user.role in ['superadmin', 'admin'] and (user.role == 'superadmin' or certificate.issuer == user):
        certificate.is_revoked = True
        certificate.save()
        return Response({"status": "certificate revoked"}, status=status.HTTP_200_OK)

    return Response({"detail": "You do not have permission to revoke this certificate."},
                    status=status.HTTP_403_FORBIDDEN)
