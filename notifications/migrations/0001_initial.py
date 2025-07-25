# Generated by Django 5.0.1 on 2025-07-20 06:02

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(max_length=50, unique=True, verbose_name='Bildirishnoma turi')),
                ('subject_template', models.CharField(max_length=255, verbose_name='Mavzu shabloni')),
                ('body_template', models.TextField(verbose_name='Matn shabloni')),
                ('available_variables', models.TextField(blank=True, help_text='JSON format', verbose_name="Mavjud o'zgaruvchilar")),
                ('is_active', models.BooleanField(default=True, verbose_name='Faol')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Bildirishnoma shabloni',
                'verbose_name_plural': 'Bildirishnoma shablonlari',
            },
        ),
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_certificate_issued', models.BooleanField(default=True, verbose_name='Email: Sertifikat chiqarildi')),
                ('email_certificate_verified', models.BooleanField(default=True, verbose_name='Email: Sertifikat tasdiqlandi')),
                ('email_verification_request', models.BooleanField(default=True, verbose_name="Email: Tekshiruv so'rovi")),
                ('email_system_updates', models.BooleanField(default=False, verbose_name='Email: Tizim yangilanishi')),
                ('sms_certificate_issued', models.BooleanField(default=False, verbose_name='SMS: Sertifikat chiqarildi')),
                ('sms_security_alerts', models.BooleanField(default=True, verbose_name='SMS: Xavfsizlik ogohlantirishlari')),
                ('push_all_notifications', models.BooleanField(default=True, verbose_name='Push: Barcha bildirishnomalar')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bildirishnoma sozlamalari',
                'verbose_name_plural': 'Bildirishnoma sozlamalari',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('notification_type', models.CharField(choices=[('certificate_issued', 'Sertifikat chiqarildi'), ('certificate_verified', 'Sertifikat tasdiqlandi'), ('certificate_revoked', 'Sertifikat bekor qilindi'), ('verification_request', "Tekshiruv so'rovi"), ('system_update', 'Tizim yangilanishi'), ('security_alert', 'Xavfsizlik ogohlantirishi')], max_length=50, verbose_name='Turi')),
                ('channel', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('push', 'Push bildirishnoma'), ('in_app', 'Ilova ichida')], default='email', max_length=20, verbose_name='Kanal')),
                ('title', models.CharField(max_length=255, verbose_name='Sarlavha')),
                ('message', models.TextField(verbose_name='Xabar')),
                ('data', models.JSONField(blank=True, default=dict, verbose_name="Qo'shimcha ma'lumotlar")),
                ('status', models.CharField(choices=[('pending', 'Kutilmoqda'), ('sent', 'Yuborildi'), ('delivered', 'Yetkazildi'), ('failed', 'Muvaffaqiyatsiz'), ('read', "O'qildi")], default='pending', max_length=20, verbose_name='Holat')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='Yuborilgan')),
                ('delivered_at', models.DateTimeField(blank=True, null=True, verbose_name='Yetkazilgan')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name="O'qilgan")),
                ('retry_count', models.IntegerField(default=0, verbose_name='Qayta urinish soni')),
                ('max_retries', models.IntegerField(default=3, verbose_name='Maksimal urinishlar')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bildirishnoma',
                'verbose_name_plural': 'Bildirishnomalar',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['recipient', 'status'], name='notificatio_recipie_e285de_idx'), models.Index(fields=['notification_type', 'created_at'], name='notificatio_notific_f2e0f7_idx')],
            },
        ),
    ]
