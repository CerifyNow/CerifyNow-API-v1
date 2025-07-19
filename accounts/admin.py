from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Shaxsiy maʼlumotlar'), {'fields': ('first_name', 'last_name', 'phone', 'date_of_birth', 'address', 'avatar')}),
        (_('Muassasa maʼlumotlari'), {'fields': ('institution_name', 'institution_license', 'institution_address')}),
        (_('Ruxsatlar'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('Muhim sana'), {'fields': ('last_login', 'date_joined')}),
        (_('Rol'), {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('email', 'full_name', 'role', 'is_verified', 'is_staff', 'created_at')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'institution_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    def full_name(self, obj):
        return obj.full_name


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'faculty', 'specialty', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'university', 'faculty')
    readonly_fields = ('created_at', 'updated_at')
