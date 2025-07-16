from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from certificates.models import Certificate
from organizations.models import Organization

User = get_user_model()

class DashboardStats(models.Model):
    """Model to cache dashboard statistics"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_stats')
    
    # Certificate stats
    total_certificates = models.IntegerField(default=0)
    verified_certificates = models.IntegerField(default=0)
    pending_certificates = models.IntegerField(default=0)
    revoked_certificates = models.IntegerField(default=0)
    
    # Monthly stats
    certificates_this_month = models.IntegerField(default=0)
    verifications_this_month = models.IntegerField(default=0)
    
    # Activity stats
    total_verifications = models.IntegerField(default=0)
    successful_verifications = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Dashboard statistikasi')
        verbose_name_plural = _('Dashboard statistikalari')

class SystemStats(models.Model):
    """System-wide statistics"""
    date = models.DateField(unique=True)
    
    # User stats
    total_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    
    # Certificate stats
    total_certificates = models.IntegerField(default=0)
    new_certificates = models.IntegerField(default=0)
    verified_certificates = models.IntegerField(default=0)
    
    # Organization stats
    total_organizations = models.IntegerField(default=0)
    active_organizations = models.IntegerField(default=0)
    
    # Verification stats
    total_verifications = models.IntegerField(default=0)
    successful_verifications = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Tizim statistikasi')
        verbose_name_plural = _('Tizim statistikalari')
        ordering = ['-date']
