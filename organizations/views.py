from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from organizations.models import Organization, OrganizationMembership
from organizations.serializers import (
    OrganizationSerializer, OrganizationCreateSerializer,
    OrganizationMembershipSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser



class OrganizationListCreateView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Organization.objects.filter(is_active=True)
    filterset_fields = ['organization_type', 'is_verified', 'city', 'region']
    search_fields = ['name', 'short_name', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @extend_schema(
        summary="List or Create Organizations",
        description="Authenticated users can list organizations. Admins can create new organizations.",
        request=OrganizationCreateSerializer,
        responses={
            200: OpenApiResponse(response=OrganizationSerializer, description="List of organizations"),
            201: OpenApiResponse(response=OrganizationSerializer, description="New organization created"),
            400: OpenApiResponse(description="Invalid input")
        },
        tags=["Organization"]
    )
    
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
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [permissions.IsAuthenticated]
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @extend_schema(
        summary="Retrieve, Update, or Delete Organization",
        description="Retrieve, update or delete a specific organization by ID.",
        responses={
            200: OpenApiResponse(response=OrganizationSerializer),
            404: OpenApiResponse(description="Organization not found"),
            403: OpenApiResponse(description="Permission denied")
        },
        tags=["Organization"]
    )
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

class OrganizationMembershipListView(generics.ListAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = OrganizationMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List Members of an Organization",
        description="Returns a list of all active members of a specific organization.",
        parameters=[
            OpenApiParameter(name="organization_id", required=True, type=str, location=OpenApiParameter.PATH),
        ],
        responses={
            200: OpenApiResponse(response=OrganizationMembershipSerializer, description="List of members"),
            404: OpenApiResponse(description="Organization not found")
        },
        tags=["Organization Membership"]
    )
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
