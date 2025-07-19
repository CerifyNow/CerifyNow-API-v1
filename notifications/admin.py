from django.contrib import admin
from .models import Notification, NotificationTemplate, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'recipient',
        'notification_type',
        'channel',
        'status',
        'created_at',
        'sent_at',
        'read_at',
    )
    list_filter = ('notification_type', 'channel', 'status', 'created_at')
    search_fields = ('title', 'recipient__email', 'message')
    readonly_fields = (
        'id',
        'created_at',
        'sent_at',
        'delivered_at',
        'read_at',
        'retry_count',
    )
    autocomplete_fields = ('recipient',)
    ordering = ('-created_at',)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'notification_type',
        'is_active',
        'created_at',
        'updated_at',
    )
    list_filter = ('is_active',)
    search_fields = ('notification_type', 'subject_template')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_certificate_issued', 'sms_certificate_issued', 'push_all_notifications')
    list_filter = ('email_certificate_issued', 'sms_certificate_issued', 'push_all_notifications')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('user',)
