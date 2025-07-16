from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['notification_type', 'channel', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

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

class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference

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
