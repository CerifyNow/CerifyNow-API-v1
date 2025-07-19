from rest_framework.permissions import BasePermission, SAFE_METHODS

class UserPermissions(BasePermission):
    """
      - superadmin: barcha action
      - institutions: hech narsa qila olmaydi
      - student: faqat readonly (GET, HEAD, OPTIONS)
      """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role == "superadmin":
            return True

        if user.role == 'institutions':
            return False

        # student: faqat readonly
        if user.role == 'student':
            return request.method in SAFE_METHODS

        return False