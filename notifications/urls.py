from django.urls import path
from .views import (
    NotificationListView, mark_notification_read, mark_all_read,
    NotificationPreferenceView, notification_stats
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<uuid:notification_id>/read/', mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', mark_all_read, name='mark-all-read'),
    path('preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
    path('stats/', notification_stats, name='notification-stats'),
]
