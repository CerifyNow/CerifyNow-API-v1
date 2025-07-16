from rest_framework import permissions

class IsOwnerOrIssuerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners, issuers or admins to view/edit certificates.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.role == 'admin':
            return True
        
        # Owner can view their certificates
        if obj.holder == request.user:
            return request.method in permissions.SAFE_METHODS
        
        # Issuer can view and edit their issued certificates
        if obj.issuer == request.user:
            return True
        
        return False

class IsOrganizationOrAdmin(permissions.BasePermission):
    """
    Permission to only allow organizations or admins.
    """
    
    def has_permission(self, request, view):
        return request.user.role in ['organization', 'admin']
