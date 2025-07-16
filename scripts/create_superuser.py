#!/usr/bin/env python
"""
Script to create a superuser for CerifyNow platform
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certifynow.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    """Create a superuser if it doesn't exist"""
    email = 'admin@certifynow.uz'
    password = 'admin123'
    
    if not User.objects.filter(email=email).exists():
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
        print(f'Superuser created: {email}')
        print(f'Password: {password}')
    else:
        print('Superuser already exists')

if __name__ == '__main__':
    create_superuser()
