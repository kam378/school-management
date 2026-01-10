from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from myapps.student.models import StudentProfile
from django.db import connection

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates missing StudentProfile records for users with role="student"'

    def handle(self, *args, **options):
        # Handle tenants if using django-tenants
        # But this command usually runs on a specific schema or public
        # We assume standard run
        
        self.stdout.write("Checking for students without profiles...")
        
        students = User.objects.filter(role='student')
        count = 0
        created_count = 0
        
        for student in students:
            count += 1
            profile, created = StudentProfile.objects.get_or_create(user=student)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created profile for {student.username}"))
            else:
                pass
                # self.stdout.write(f"Profile already exists for {student.username}")
        
        self.stdout.write(self.style.SUCCESS(f"checked {count} students. Created {created_count} new profiles."))
