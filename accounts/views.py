from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.permissions import UserPermissions
from accounts.serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    UserSerializer, PasswordChangeSerializer
)

User = get_user_model()

@extend_schema(
    summary="User Registration",
    description="Foydalanuvchini ro'yxatdan o'tkazadi va JWT tokenlarni qaytaradi.",
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description="Muvaffaqiyatli ro'yxatdan o'tildi"
        ),
        400: OpenApiResponse(description="Xatolik: noto‘g‘ri ma’lumot")
    },
    tags=["Authentication"]
)

class RegisterView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz'
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [AllowAny, UserPermissions]
    serializer_class = UserLoginSerializer

    @extend_schema(
        summary="User Login",
        description="Foydalanuvchini tizimga kirgizadi va JWT tokenlarni qaytaradi.",
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=UserSerializer,
                description="Muvaffaqiyatli tizimga kirildi"
            ),
            400: OpenApiResponse(description="Login yoki parol xato")
        },
        tags=["Authentication"]
    )
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Muvaffaqiyatli kirdingiz'
        })

@extend_schema(
    summary="Access tokenni yangilash",
    description="Refresh token orqali yangi access token olinadi.",
    request=TokenRefreshSerializer,
    responses={
        200: OpenApiResponse(
            response=None,
            description="Yangi access token"
        ),
        401: OpenApiResponse(description="Refresh token yaroqsiz yoki muddati tugagan")
    },
    tags=["Authentication"]
)
class CustomTokenRefreshView(TokenRefreshView):
    pass

@extend_schema(
    summary="Get or Update User Profile",
    description="Foydalanuvchi o‘z profilini ko‘rishi yoki yangilashi mumkin.",
    responses={
        200: OpenApiResponse(response=UserSerializer, description="Foydalanuvchi profili"),
        401: OpenApiResponse(description="Avtorizatsiya kerak")
    },
    tags=["Authentication"]
)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get or Update User Profile",
        description="Foydalanuvchi o‘z profilini ko‘rishi yoki yangilashi mumkin.",
        responses={
            200: OpenApiResponse(response=UserSerializer, description="Foydalanuvchi profili"),
            401: OpenApiResponse(description="Avtorizatsiya kerak")
        },
        tags=["Authentication"]
    )
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Parol muvaffaqiyatli o\'zgartirildi'
        })

@extend_schema(
    summary="User Logout",
    description="Foydalanuvchini tizimdan chiqaradi va refresh tokenni blacklist qiladi.",
    request=OpenApiTypes.OBJECT,
    responses={
        200: OpenApiResponse(description="Muvaffaqiyatli chiqildi"),
        400: OpenApiResponse(description="Xatolik yuz berdi"),
        401: OpenApiResponse(description="Avtorizatsiya kerak")
    },
    tags=["Authentication"]
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Muvaffaqiyatli chiqildi'})
    except Exception as e:
        return Response({'error': 'Xatolik yuz berdi'}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="List of Users",
    description="Adminlar barcha foydalanuvchilarni ko‘rishi mumkin, boshqa foydalanuvchilar esa faqat o‘z ma'lumotlarini.",
    parameters=[
        OpenApiParameter(name='role', type=str, location=OpenApiParameter.QUERY, required=False, description="Foydalanuvchi roli"),
        OpenApiParameter(name='is_verified', type=bool, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='is_active', type=bool, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='search', type=str, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='ordering', type=str, location=OpenApiParameter.QUERY, required=False, description="Tartiblash: `created_at`, `first_name`, `last_name`")
    ],
    responses={
        200: OpenApiResponse(response=UserSerializer, description="Foydalanuvchilar ro'yxati"),
        401: OpenApiResponse(description="Avtorizatsiya kerak")
    },
    tags=["Authentication"]
)
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'is_verified', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'organization_name']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Only admins can see all users
        if self.request.user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
