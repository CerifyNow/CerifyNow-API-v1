from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('certificate_issued', _('Sertifikat chiqarildi')),
        ('certificate_verified', _('Sertifikat tasdiqlandi')),
        ('certificate_revoked', _('Sertifikat bekor qilindi')),
        ('verification_request', _('Tekshiruv so\'rovi')),
        ('system_update', _('Tizim yangilanishi')),
        ('security_alert', _('Xavfsizlik ogohlantirishi')),
    ]
    
    CHANNELS = [
        ('email', _('Email')),
        ('sms', _('SMS')),
        ('push', _('Push bildirishnoma')),
        ('in_app', _('Ilova ichida')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Kutilmoqda')),
        ('sent', _('Yuborildi')),
        ('delivered', _('Yetkazildi')),
        ('failed', _('Muvaffaqiyatsiz')),
        ('read', _('O\'qildi')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(_('Turi'), max_length=50, choices=NOTIFICATION_TYPES)
    channel = models.CharField(_('Kanal'), max_length=20, choices=CHANNELS, default='email')
    
    title = models.CharField(_('Sarlavha'), max_length=255)
    message = models.TextField(_('Xabar'))
    
    # Additional data as JSON
    data = models.JSONField(_('Qo\'shimcha ma\'lumotlar'), default=dict, blank=True)
    
    status = models.CharField(_('Holat'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(_('Yaratilgan'), auto_now_add=True)
    sent_at = models.DateTimeField(_('Yuborilgan'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('Yetkazilgan'), null=True, blank=True)
    read_at = models.DateTimeField(_('O\'qilgan'), null=True, blank=True)
    
    # Retry mechanism
    retry_count = models.IntegerField(_('Qayta urinish soni'), default=0)
    max_retries = models.IntegerField(_('Maksimal urinishlar'), default=3)
    
    class Meta:
        verbose_name = _('Bildirishnoma')
        verbose_name_plural = _('Bildirishnomalar')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['notification_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.email}"

class NotificationTemplate(models.Model):
    """Email/SMS templates for notifications"""
    notification_type = models.CharField(_('Bildirishnoma turi'), max_length=50, unique=True)
    subject_template = models.CharField(_('Mavzu shabloni'), max_length=255)
    body_template = models.TextField(_('Matn shabloni'))
    
    # Template variables help text
    available_variables = models.TextField(_('Mavjud o\'zgaruvchilar'), blank=True, help_text=_('JSON format'))
    
    is_active = models.BooleanField(_('Faol'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Bildirishnoma shabloni')
        verbose_name_plural = _('Bildirishnoma shablonlari')
    
    def __str__(self):
        return f"Template: {self.notification_type}"

class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_certificate_issued = models.BooleanField(_('Email: Sertifikat chiqarildi'), default=True)
    email_certificate_verified = models.BooleanField(_('Email: Sertifikat tasdiqlandi'), default=True)
    email_verification_request = models.BooleanField(_('Email: Tekshiruv so\'rovi'), default=True)
    email_system_updates = models.BooleanField(_('Email: Tizim yangilanishi'), default=False)
    
    # SMS preferences
    sms_certificate_issued = models.BooleanField(_('SMS: Sertifikat chiqarildi'), default=False)
    sms_security_alerts = models.BooleanField(_('SMS: Xavfsizlik ogohlantirishlari'), default=True)
    
    # Push notification preferences
    push_all_notifications = models.BooleanField(_('Push: Barcha bildirishnomalar'), default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Bildirishnoma sozlamalari')
        verbose_name_plural = _('Bildirishnoma sozlamalari')
