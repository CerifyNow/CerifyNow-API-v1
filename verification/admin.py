from django.contrib import admin
from .models import VerificationRequest, VerificationLog


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'certificate',
        'requester_email',
        'requester_ip',
        'verification_result',
        'verification_method',
        'verification_date',
    )
    list_filter = ('verification_result', 'verification_method', 'verification_date')
    search_fields = (
        'certificate__code',
        'requester_email',
        'requester_organization',
        'requester_ip',
    )
    date_hierarchy = 'verification_date'
    ordering = ('-verification_date',)
    readonly_fields = ('verification_date',)


@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = (
        'certificate',
        'user',
        'action',
        'ip_address',
        'timestamp',
    )
    list_filter = ('action', 'timestamp')
    search_fields = (
        'certificate__code',
        'user__email',
        'ip_address',
    )
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
