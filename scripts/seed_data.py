#!/usr/bin/env python
"""
Script to seed the database with sample data
"""
import os
import sys
import django
from datetime import date, timedelta
import random

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certifynow.settings')
django.setup()

from django.contrib.auth import get_user_model
from certificates.models import Certificate
from organizations.models import Organization

User = get_user_model()

def create_sample_users():
    """Create sample users"""
    users_data = [
        {
            'username': 'alisher_student',
            'email': 'alisher@student.uz',
            'first_name': 'Alisher',
            'last_name': 'Karimov',
            'role': 'student',
            'phone': '+998901234567'
        },
        {
            'username': 'malika_student',
            'email': 'malika@student.uz',
            'first_name': 'Malika',
            'last_name': 'Tosheva',
            'role': 'student',
            'phone': '+998901234568'
        },
        {
            'username': 'tdtu_org',
            'email': 'admin@tdtu.uz',
            'first_name': 'TDTU',
            'last_name': 'Administrator',
            'role': 'organization',
            'organization_name': 'Toshkent Davlat Texnika Universiteti',
            'organization_license': 'EDU-001-2020'
        },
        {
            'username': 'itacademy_org',
            'email': 'admin@itacademy.uz',
            'first_name': 'IT Academy',
            'last_name': 'Administrator',
            'role': 'organization',
            'organization_name': 'IT Academy Uzbekistan',
            'organization_license': 'EDU-002-2021'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        if not User.objects.filter(email=user_data['email']).exists():
            user = User.objects.create_user(
                password='password123',
                is_verified=True,
                **user_data
            )
            created_users.append(user)
            print(f'Created user: {user.email}')
    
    return created_users

def create_sample_organizations():
    """Create sample organizations"""
    orgs_data = [
        {
            'name': 'Toshkent Davlat Texnika Universiteti',
            'short_name': 'TDTU',
            'organization_type': 'university',
            'email': 'info@tdtu.uz',
            'phone': '+998712345678',
            'address': 'Universitetskaya ko\'chasi 2, Toshkent',
            'city': 'Toshkent',
            'region': 'Toshkent',
            'license_number': 'EDU-001-2020',
            'is_verified': True
        },
        {
            'name': 'IT Academy Uzbekistan',
            'short_name': 'IT Academy',
            'organization_type': 'training_center',
            'email': 'info@itacademy.uz',
            'phone': '+998712345679',
            'address': 'Amir Temur ko\'chasi 108, Toshkent',
            'city': 'Toshkent',
            'region': 'Toshkent',
            'license_number': 'EDU-002-2021',
            'is_verified': True
        }
    ]
    
    created_orgs = []
    for org_data in orgs_data:
        if not Organization.objects.filter(email=org_data['email']).exists():
            org = Organization.objects.create(**org_data)
            created_orgs.append(org)
            print(f'Created organization: {org.name}')
    
    return created_orgs

def create_sample_certificates():
    """Create sample certificates"""
    students = User.objects.filter(role='student')
    organizations = User.objects.filter(role='organization')
    
    if not students.exists() or not organizations.exists():
        print('No students or organizations found. Please create users first.')
        return
    
    certificates_data = [
        {
            'title': 'Bakalavr Diplomi',
            'description': 'Dasturiy ta\'minot muhandisligi bo\'yicha bakalavr diplomi',
            'certificate_type': 'diploma',
            'institution_name': 'Toshkent Davlat Texnika Universiteti',
            'degree': 'Bakalavr',
            'field_of_study': 'Dasturiy ta\'minot muhandisligi',
            'grade': 'A',
            'issue_date': date.today() - timedelta(days=30),
            'status': 'issued',
            'is_verified': True
        },
        {
            'title': 'JavaScript Sertifikati',
            'description': 'JavaScript dasturlash tili bo\'yicha sertifikat',
            'certificate_type': 'certificate',
            'institution_name': 'IT Academy Uzbekistan',
            'degree': 'Sertifikat',
            'field_of_study': 'Web Development',
            'grade': 'A+',
            'issue_date': date.today() - timedelta(days=60),
            'status': 'issued',
            'is_verified': True
        },
        {
            'title': 'Python Sertifikati',
            'description': 'Python dasturlash tili bo\'yicha sertifikat',
            'certificate_type': 'certificate',
            'institution_name': 'IT Academy Uzbekistan',
            'degree': 'Sertifikat',
            'field_of_study': 'Backend Development',
            'grade': 'A',
            'issue_date': date.today() - timedelta(days=90),
            'status': 'issued',
            'is_verified': True
        }
    ]
    
    created_certificates = []
    for i, cert_data in enumerate(certificates_data):
        holder = random.choice(students)
        issuer = random.choice(organizations)
        
        certificate = Certificate.objects.create(
            holder=holder,
            issuer=issuer,
            **cert_data
        )
        created_certificates.append(certificate)
        print(f'Created certificate: {certificate.title} for {holder.full_name}')
    
    return created_certificates

def main():
    """Main function to seed data"""
    print('Starting data seeding...')
    
    # Create users
    print('\n1. Creating sample users...')
    create_sample_users()
    
    # Create organizations
    print('\n2. Creating sample organizations...')
    create_sample_organizations()
    
    # Create certificates
    print('\n3. Creating sample certificates...')
    create_sample_certificates()
    
    print('\nData seeding completed!')
    print('\nSample login credentials:')
    print('Admin: admin@certifynow.uz / admin123')
    print('Student: alisher@student.uz / password123')
    print('Organization: admin@tdtu.uz / password123')

if __name__ == '__main__':
    main()
