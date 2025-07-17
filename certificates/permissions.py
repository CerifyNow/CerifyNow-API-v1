from rest_framework import permissions


class CanCreateCertificatePermission(permissions.BasePermission):
    """
    Permission to allow only admins and students to create certificates.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.can_create_certificates


class IsOwnerOrIssuerOrCanView(permissions.BasePermission):
    """
    Permission to allow owners, issuers, or users who can view certificates.
    """

    def has_object_permission(self, request, view, obj):
        # Superadmin can view all
        if request.user.role == 'superadmin':
            return True

        # Checker can only view for verification
        if request.user.role == 'checker':
            return request.method in permissions.SAFE_METHODS

        # Owner can view their certificates
        if obj.holder == request.user:
            return True

        # Issuer can view and edit their issued certificates
        if obj.issuer == request.user:
            return True

        return False


class IsSuperAdminPermission(permissions.BasePermission):
    """
    Permission to only allow superadmins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


class IsInstitutionAdminPermission(permissions.BasePermission):
    """
    Permission to only allow institution admins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
