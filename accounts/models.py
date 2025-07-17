from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', _('Talaba')),
        ('admin', _('Muassasa Administratori')),
        ('superadmin', _('Super Administrator')),
        ('checker', _('Tekshiruvchi')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('Email manzil'), unique=True)
    phone = models.CharField(_('Telefon raqam'), max_length=20, blank=True)
    role = models.CharField(_('Rol'), max_length=20, choices=ROLE_CHOICES, default='student')
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(_('Tasdiqlangan'), default=False)
    date_of_birth = models.DateField(_('Tug\'ilgan sana'), blank=True, null=True)
    address = models.TextField(_('Manzil'), blank=True)

    # Additional fields for institution admins
    institution_name = models.CharField(_('Muassasa nomi'), max_length=255, blank=True)
    institution_license = models.CharField(_('Litsenziya raqami'), max_length=100, blank=True)
    institution_address = models.TextField(_('Muassasa manzili'), blank=True)

    created_at = models.DateTimeField(_('Yaratilgan vaqt'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yangilangan vaqt'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('Foydalanuvchi')
        verbose_name_plural = _('Foydalanuvchilar')

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def can_create_certificates(self):
        """Check if user can create certificates"""
        return self.role in ['admin', 'student']

    @property
    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role == 'superadmin'

    @property
    def can_verify_only(self):
        """Check if user can only verify certificates"""
        return self.role == 'checker'

    @property
    def is_institution_admin(self):
        """Check if user is institution admin"""
        return self.role == 'admin'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('Biografiya'), blank=True)
    website = models.URLField(_('Veb-sayt'), blank=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True)
    telegram = models.CharField(_('Telegram'), max_length=100, blank=True)

    # Student specific fields
    student_id = models.CharField(_('Talaba ID'), max_length=50, blank=True)
    university = models.CharField(_('Universitet'), max_length=255, blank=True)
    faculty = models.CharField(_('Fakultet'), max_length=255, blank=True)
    specialty = models.CharField(_('Mutaxassislik'), max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Foydalanuvchi profili')
        verbose_name_plural = _('Foydalanuvchi profillari')
