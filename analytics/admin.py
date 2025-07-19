from django.contrib import admin
from .models import DashboardStats, SystemStats


@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'total_certificates',
        'verified_certificates',
        'pending_certificates',
        'revoked_certificates',
        'certificates_this_month',
        'verifications_this_month',
        'total_verifications',
        'successful_verifications',
        'last_updated',
    )
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('last_updated',)


@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'total_users',
        'active_users',
        'new_users',
        'total_certificates',
        'new_certificates',
        'verified_certificates',
        'total_organizations',
        'active_organizations',
        'total_verifications',
        'successful_verifications',
        'created_at',
    )
    list_filter = ('date',)
    readonly_fields = ('created_at',)
    ordering = ('-date',)
