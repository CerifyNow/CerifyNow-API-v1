from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser for CerifyNow platform'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Admin email address')
        parser.add_argument('--password', type=str, help='Admin password')

    def handle(self, *args, **options):
        email = options.get('email') or 'admin@certifynow.uz'
        password = options.get('password') or 'admin123'
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            return
        
        user = User.objects.create_user(
            username='admin',
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator',
            role='admin',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created superuser: {email}')
        )
        self.stdout.write(f'Password: {password}')
