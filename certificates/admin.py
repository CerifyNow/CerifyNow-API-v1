from django.contrib import admin
from .models import Certificate, CertificateTemplate, CertificateVerification


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = (
        'certificate_id',
        'title',
        'holder',
        'issuer',
        'status',
        'is_verified',
        'issue_date',
        'created_at',
    )
    list_filter = ('status', 'is_verified', 'issue_date', 'created_at')
    search_fields = ('certificate_id', 'title', 'holder__email', 'issuer__email')
    readonly_fields = ('created_at', 'updated_at', 'blockchain_hash', 'blockchain_transaction', 'qr_code')
    autocomplete_fields = ('holder', 'issuer')
    ordering = ('-created_at',)


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('created_by',)


@admin.register(CertificateVerification)
class CertificateVerificationAdmin(admin.ModelAdmin):
    list_display = (
        'certificate',
        'verifier_ip',
        'verification_date',
        'is_valid',
    )
    list_filter = ('is_valid', 'verification_date')
    search_fields = ('certificate__certificate_id', 'verifier_ip')
    readonly_fields = ('verification_date',)
