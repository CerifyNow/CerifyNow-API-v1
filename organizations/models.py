from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()

class Organization(models.Model):
    ORGANIZATION_TYPES = [
        ('university', _('Universitet')),
        ('college', _('Kollej')),
        ('institute', _('Institut')),
        ('academy', _('Akademiya')),
        ('school', _('Maktab')),
        ('training_center', _('O\'quv markazi')),
        ('certification_body', _('Sertifikatlashtirish organi')),
        ('government', _('Davlat muassasasi')),
        ('private', _('Xususiy tashkilot')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Nomi'), max_length=255)
    short_name = models.CharField(_('Qisqa nomi'), max_length=100, blank=True)
    organization_type = models.CharField(_('Turi'), max_length=50, choices=ORGANIZATION_TYPES)
    
    # Contact Information
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Telefon'), max_length=20)
    website = models.URLField(_('Veb-sayt'), blank=True)
    
    # Address
    address = models.TextField(_('Manzil'))
    city = models.CharField(_('Shahar'), max_length=100)
    region = models.CharField(_('Viloyat'), max_length=100)
    postal_code = models.CharField(_('Pochta indeksi'), max_length=20, blank=True)
    country = models.CharField(_('Mamlakat'), max_length=100, default='O\'zbekiston')
    
    # Legal Information
    license_number = models.CharField(_('Litsenziya raqami'), max_length=100, blank=True)
    tax_id = models.CharField(_('Soliq ID'), max_length=50, blank=True)
    registration_number = models.CharField(_('Ro\'yxat raqami'), max_length=100, blank=True)
    
    # Status
    is_verified = models.BooleanField(_('Tasdiqlangan'), default=False)
    is_active = models.BooleanField(_('Faol'), default=True)
    
    # Relationships
    admin_users = models.ManyToManyField(User, related_name='administered_organizations', blank=True)
    
    # Metadata
    logo = models.ImageField(_('Logo'), upload_to='organization_logos/', blank=True, null=True)
    description = models.TextField(_('Tavsif'), blank=True)
    established_date = models.DateField(_('Tashkil etilgan sana'), blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Tashkilot')
        verbose_name_plural = _('Tashkilotlar')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class OrganizationMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('issuer', _('Sertifikat chiqaruvchi')),
        ('viewer', _('Ko\'ruvchi')),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(_('Rol'), max_length=20, choices=ROLE_CHOICES, default='viewer')
    
    is_active = models.BooleanField(_('Faol'), default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Tashkilot a\'zoligi')
        verbose_name_plural = _('Tashkilot a\'zoliklari')
        unique_together = ['organization', 'user']
