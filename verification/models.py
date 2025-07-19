from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from certificates.models import Certificate

User = get_user_model()


class VerificationRequest(models.Model):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='verification_requests')
    requester_ip = models.GenericIPAddressField(_('So\'rovchi IP'))
    requester_user_agent = models.TextField(_('User Agent'), blank=True)
    requester_email = models.EmailField(_('So\'rovchi email'), blank=True)
    requester_organization = models.CharField(_('So\'rovchi tashkilot'), max_length=255, blank=True)

    verification_result = models.BooleanField(_('Tekshiruv natijasi'), default=True)
    verification_date = models.DateTimeField(_('Tekshiruv vaqti'), auto_now_add=True)

    # Additional verification details
    verification_method = models.CharField(_('Tekshiruv usuli'), max_length=50, default='web')  # web, api, qr
    verification_location = models.CharField(_('Joylashuv'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('Tekshiruv so\'rovi')
        verbose_name_plural = _('Tekshiruv so\'rovlari')
        ordering = ['-verification_date']


class VerificationLog(models.Model):
    ACTION_CHOICES = [
        ('verify', _('Tekshirish')),
        ('download', _('Yuklab olish')),
        ('share', _('Ulashish')),
        ('view', _('Ko\'rish')),
    ]

    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(_('Harakat'), max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(_('IP manzil'))
    user_agent = models.TextField(_('User Agent'), blank=True)
    timestamp = models.DateTimeField(_('Vaqt'), auto_now_add=True)

    # Additional context
    details = models.JSONField(_('Tafsilotlar'), default=dict, blank=True)

    class Meta:
        verbose_name = _('Tekshiruv logi')
        verbose_name_plural = _('Tekshiruv loglari')
        ordering = ['-timestamp']
