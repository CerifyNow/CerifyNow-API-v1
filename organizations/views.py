from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Organization, OrganizationMembership
from .serializers import (
    OrganizationSerializer, OrganizationCreateSerializer,
    OrganizationMembershipSerializer
)

class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset = Organization.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['organization_type', 'is_verified', 'city', 'region']
    search_fields = ['name', 'short_name', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrganizationCreateSerializer
        return OrganizationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Organization.objects.all()
        elif user.role == 'organization':
            return Organization.objects.filter(admin_users=user)
        else:
            return Organization.objects.filter(is_verified=True, is_active=True)

class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

class OrganizationMembershipListView(generics.ListAPIView):
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        organization_id = self.kwargs.get('organization_id')
        return OrganizationMembership.objects.filter(
            organization_id=organization_id,
            is_active=True
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_organization(request, organization_id):
    """Join an organization"""
    try:
        organization = Organization.objects.get(id=organization_id)
        
        # Check if user is already a member
        if OrganizationMembership.objects.filter(
            organization=organization,
            user=request.user,
            is_active=True
        ).exists():
            return Response(
                {'error': 'Siz allaqachon bu tashkilot a\'zosisiz'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create membership
        membership = OrganizationMembership.objects.create(
            organization=organization,
            user=request.user,
            role='viewer'  # Default role
        )
        
        serializer = OrganizationMembershipSerializer(membership)
        return Response({
            'message': 'Tashkilotga muvaffaqiyatli qo\'shildingiz',
            'membership': serializer.data
        })
        
    except Organization.DoesNotExist:
        return Response(
            {'error': 'Tashkilot topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_organization(request, organization_id):
    """Leave an organization"""
    try:
        membership = OrganizationMembership.objects.get(
            organization_id=organization_id,
            user=request.user,
            is_active=True
        )
        
        membership.is_active = False
        membership.save()
        
        return Response({'message': 'Tashkilotdan muvaffaqiyatli chiqildi'})
        
    except OrganizationMembership.DoesNotExist:
        return Response(
            {'error': 'Siz bu tashkilot a\'zosi emassiz'},
            status=status.HTTP_404_NOT_FOUND
        )
