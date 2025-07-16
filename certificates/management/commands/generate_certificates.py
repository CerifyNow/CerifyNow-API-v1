from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from certificates.models import Certificate
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate sample certificates for testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Number of certificates to generate')

    def handle(self, *args, **options):
        count = options['count']
        
        students = list(User.objects.filter(role='student'))
        organizations = list(User.objects.filter(role='organization'))
        
        if not students or not organizations:
            self.stdout.write(
                self.style.ERROR('No students or organizations found. Please create users first.')
            )
            return
        
        certificate_types = ['diploma', 'certificate', 'license', 'award']
        institutions = [
            'Toshkent Davlat Universiteti',
            'Samarqand Davlat Universiteti',
            'Buxoro Davlat Universiteti',
            'IT Academy',
            'EPAM University',
            'Inha University',
        ]
        degrees = [
            'Bakalavr - Dasturiy ta\'minot muhandisligi',
            'Magistr - Kompyuter tizimlari',
            'JavaScript Developer',
            'Python Developer',
            'Data Science',
            'Cyber Security',
        ]
        grades = ['A+', 'A', 'A-', 'B+', 'B', '5', '4', '3']
        
        created_count = 0
        
        for i in range(count):
            try:
                certificate = Certificate.objects.create(
                    holder=random.choice(students),
                    issuer=random.choice(organizations),
                    title=f"{random.choice(['Diplom', 'Sertifikat', 'Guvohnoma'])} #{i+1}",
                    description=f"Test sertifikat #{i+1}",
                    certificate_type=random.choice(certificate_types),
                    institution_name=random.choice(institutions),
                    degree=random.choice(degrees),
                    field_of_study=random.choice(['IT', 'Engineering', 'Business', 'Design']),
                    grade=random.choice(grades),
                    issue_date=date.today() - timedelta(days=random.randint(1, 365)),
                    expiry_date=date.today() + timedelta(days=random.randint(365, 1825)),
                    status='issued',
                    is_verified=random.choice([True, True, True, False]),  # 75% verified
                )
                created_count += 1
                
                if created_count % 10 == 0:
                    self.stdout.write(f'Created {created_count} certificates...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating certificate {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} certificates')
        )
