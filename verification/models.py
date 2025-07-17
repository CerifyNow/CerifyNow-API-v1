from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import hashlib
import json

User = get_user_model()


class Certificate(models.Model):
    STATUS_CHOICES = [
        ('draft', _('Qoralama')),
        ('issued', _('Chiqarilgan')),
        ('verified', _('Tasdiqlangan')),
        ('revoked', _('Bekor qilingan')),
    ]

    TYPE_CHOICES = [
        ('diploma', _('Diplom')),
        ('certificate', _('Sertifikat')),
        ('license', _('Litsenziya')),
        ('award', _('Mukofot')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_id = models.CharField(_('Sertifikat ID'), max_length=50, unique=True)

    # Relationships
    holder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates', verbose_name=_('Egasi'))
    issuer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_certificates',
                               verbose_name=_('Chiqaruvchi'))

    # Certificate Details
    title = models.CharField(_('Sarlavha'), max_length=255)
    description = models.TextField(_('Tavsif'), blank=True)
    certificate_type = models.CharField(_('Turi'), max_length=20, choices=TYPE_CHOICES, default='certificate')

    # Academic Information
    institution_name = models.CharField(_('Muassasa nomi'), max_length=255)
    institution_address = models.TextField(_('Muassasa manzili'), blank=True)
    degree = models.CharField(_('Daraja/Kurs'), max_length=255, blank=True)
    field_of_study = models.CharField(_('Ta\'lim yo\'nalishi'), max_length=255, blank=True)
    grade = models.CharField(_('Baho'), max_length=10, blank=True)

    # Dates
    issue_date = models.DateField(_('Chiqarilgan sana'))
    expiry_date = models.DateField(_('Amal qilish muddati'), blank=True, null=True)

    # Status and Verification
    status = models.CharField(_('Holat'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_verified = models.BooleanField(_('Tasdiqlangan'), default=False)

    # Files
    certificate_file = models.FileField(_('Sertifikat fayli'), upload_to='certificates/', blank=True, null=True)
    qr_code = models.ImageField(_('QR kod'), upload_to='qr_codes/', blank=True, null=True)

    # Blockchain
    blockchain_hash = models.CharField(_('Blokcheyn hash'), max_length=255, blank=True)
    blockchain_transaction = models.CharField(_('Tranzaksiya ID'), max_length=255, blank=True)

    # Metadata
    metadata = models.JSONField(_('Qo\'shimcha ma\'lumotlar'), default=dict, blank=True)

    created_at = models.DateTimeField(_('Yaratilgan vaqt'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yangilangan vaqt'), auto_now=True)

    class Meta:
        verbose_name = _('Sertifikat')
        verbose_name_plural = _('Sertifikatlar')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.holder.full_name}"

    def save(self, *args, **kwargs):
        # Generate certificate ID if not exists
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"

        # Generate blockchain hash
        if not self.blockchain_hash:
            self.blockchain_hash = self.generate_blockchain_hash()

        super().save(*args, **kwargs)

        # Generate QR code after saving
        if not self.qr_code:
            self.generate_qr_code()

    def generate_blockchain_hash(self):
        """Generate a blockchain hash for certificate verification"""
        data = {
            'certificate_id': self.certificate_id,
            'holder_email': self.holder.email if self.holder else '',
            'issuer_email': self.issuer.email if self.issuer else '',
            'title': self.title,
            'institution_name': self.institution_name,
            'issue_date': str(self.issue_date) if self.issue_date else '',
            'degree': self.degree,
            'grade': self.grade,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def generate_qr_code(self):
        """Generate QR code for certificate verification using blockchain hash"""
        # QR code contains the blockchain hash for verification
        qr_data = f"https://certifynow.uz/verify?hash={self.blockchain_hash}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Save to model
        filename = f'qr_{self.certificate_id}_{self.blockchain_hash[:8]}.png'
        self.qr_code.save(filename, File(buffer), save=False)

        # Update the record without triggering save() again
        Certificate.objects.filter(id=self.id).update(qr_code=self.qr_code)

    def verify_hash(self):
        """Verify if the stored hash matches the generated hash"""
        expected_hash = self.generate_blockchain_hash()
        return self.blockchain_hash == expected_hash

    @property
    def qr_verification_url(self):
        """Get the QR verification URL"""
        return f"https://certifynow.uz/verify?hash={self.blockchain_hash}"


class CertificateTemplate(models.Model):
    name = models.CharField(_('Shablon nomi'), max_length=255)
    description = models.TextField(_('Tavsif'), blank=True)
    template_file = models.FileField(_('Shablon fayli'), upload_to='templates/')
    is_active = models.BooleanField(_('Faol'), default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Yaratuvchi'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Sertifikat shabloni')
        verbose_name_plural = _('Sertifikat shablonlari')


class CertificateVerification(models.Model):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='verifications')
    verifier_ip = models.GenericIPAddressField(_('Tekshiruvchi IP'))
    verifier_user_agent = models.TextField(_('User Agent'), blank=True)
    verification_date = models.DateTimeField(_('Tekshiruv vaqti'), auto_now_add=True)
    is_valid = models.BooleanField(_('Haqiqiy'), default=True)
    verification_method = models.CharField(_('Tekshiruv usuli'), max_length=20, default='web')

    class Meta:
        verbose_name = _('Sertifikat tekshiruvi')
        verbose_name_plural = _('Sertifikat tekshiruvlari')
        ordering = ['-verification_date']
