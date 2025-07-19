from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer

@extend_schema(
    summary="Foydalanuvchining bildirishnomalar ro'yxati",
    description="Foydalanuvchiga yuborilgan barcha bildirishnomalarni filtrlab olish imkonini beradi.",
    parameters=[
        OpenApiParameter(name="notification_type", required=False, type=str),
        OpenApiParameter(name="channel", required=False, type=str),
        OpenApiParameter(name="status", required=False, type=str),
    ],
    responses={200: NotificationSerializer(many=True)},
    tags=["Notifications"]
)

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['notification_type', 'channel', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


@extend_schema(
    summary="Bitta bildirishnomani o‘qilgan deb belgilash",
    description="Foydalanuvchi belgilangan `notification_id` bo‘yicha bildirishnomani o‘qilgan deb belgilaydi.",
    responses={200: OpenApiResponse(description="Success read")},
    tags=["Notifications"]
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.status = 'read'
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({'message': 'Bildirishnoma o\'qilgan deb belgilandi'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Bildirishnoma topilmadi'},
            status=status.HTTP_404_NOT_FOUND
        )


@extend_schema(
    summary="Barcha bildirishnomalarni o‘qilgan deb belgilash",
    description="Foydalanuvchining barcha yuborilgan yoki yetkazilgan bildirishnomalarini o‘qilgan deb belgilaydi.",
    responses={200: OpenApiResponse(description="Success message")},
    tags=["Notifications"]
)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(
        recipient=request.user,
        status__in=['sent', 'delivered']
    ).update(
        status='read',
        read_at=timezone.now()
    )
    
    return Response({'message': 'Barcha bildirishnomalar o\'qilgan deb belgilandi'})

@extend_schema(
    summary="Bildirishnoma sozlamalarini ko‘rish va yangilash",
    description="Foydalanuvchining bildirishnoma sozlamalarini olish va yangilash imkonini beradi.",
    responses={200: NotificationPreferenceSerializer},
    tags=["Notifications"]
)

class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


@extend_schema(
    summary="Foydalanuvchi uchun bildirishnoma statistikasi",
    description="O‘qilgan, o‘qilmagan, muvaffaqiyatsiz va jami bildirishnomalar sonini qaytaradi.",
    responses={200: dict},
    tags=["Notifications"]
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_stats(request):
    """Get notification statistics"""
    user = request.user
    notifications = Notification.objects.filter(recipient=user)
    
    stats = {
        'total': notifications.count(),
        'unread': notifications.filter(status__in=['sent', 'delivered']).count(),
        'read': notifications.filter(status='read').count(),
        'failed': notifications.filter(status='failed').count(),
    }
    
    return Response(stats)
