from django.contrib import admin
from .models import Organization, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'short_name',
        'organization_type',
        'city',
        'region',
        'is_verified',
        'is_active',
        'created_at',
    )
    list_filter = ('organization_type', 'is_verified', 'is_active', 'region', 'country')
    search_fields = ('name', 'short_name', 'email', 'phone', 'tax_id', 'license_number')
    autocomplete_fields = ('admin_users',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    fieldsets = (
        (_('Asosiy maʼlumotlar'), {
            'fields': ('name', 'short_name', 'organization_type', 'description', 'logo')
        }),
        (_('Aloqa maʼlumotlari'), {
            'fields': ('email', 'phone', 'website', 'address', 'city', 'region', 'postal_code', 'country')
        }),
        (_('Yuridik maʼlumotlar'), {
            'fields': ('license_number', 'tax_id', 'registration_number', 'established_date')
        }),
        (_('Holat'), {
            'fields': ('is_verified', 'is_active', 'admin_users')
        }),
        (_('Vaqtlar'), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = (
        'organization',
        'user',
        'role',
        'is_active',
        'joined_at',
    )
    list_filter = ('role', 'is_active', 'joined_at')
    search_fields = ('organization__name', 'user__email', 'user__first_name', 'user__last_name')
    autocomplete_fields = ('organization', 'user')
    ordering = ('-joined_at',)
