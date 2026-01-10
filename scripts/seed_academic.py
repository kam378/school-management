import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from django_tenants.utils import schema_context
from myapps.accounts.models import User
from myapps.school_admin.models import GradeLevel, Subject, Classroom, ClassSubject
from myapps.teacher.models import Assignment, Grade
from django.utils import timezone
from datetime import timedelta

def seed_data(schema_name):
    print(f"Seeding academic data for schema: {schema_name}")
    with schema_context(schema_name):
        # 1. Get or Create Teacher
        teacher = User.objects.filter(role='teacher').first()
        if not teacher:
            print("No teacher found. Please create a teacher user first.")
            return

        # 2. Setup Academic structure
        grade_level, _ = GradeLevel.objects.get_or_create(name="Grade 10")
        subject, _ = Subject.objects.get_or_create(name="Mathematics", code="MATH101")
        classroom, _ = Classroom.objects.get_or_create(name="10A", level=grade_level)

        # 3. Assign students to classroom
        students = User.objects.filter(role='student')[:10]
        classroom.students.set(students)
        print(f"Added {len(students)} students to {classroom.name}")

        # 4. Link Teacher + Subject + Classroom
        cs, _ = ClassSubject.objects.get_or_create(
            classroom=classroom,
            subject=subject,
            teacher=teacher
        )
        print(f"Assigned {teacher.username} to teach {subject.name} in {classroom.name}")

        # 5. Create Assignments
        assignment1, _ = Assignment.objects.get_or_create(
            class_subject=cs,
            title="Algebra Quiz 1",
            max_score=50,
            due_date=timezone.now() + timedelta(days=5)
        )
        
        assignment2, _ = Assignment.objects.get_or_create(
            class_subject=cs,
            title="Geometry Project",
            max_score=100,
            due_date=timezone.now() + timedelta(days=15)
        )
        print("Created assignments.")

        # 6. Seed some grades
        for student in students:
            Grade.objects.get_or_create(
                assignment=assignment1,
                student=student,
                defaults={'score': 42.5 if student.id % 2 == 0 else 38.0, 'remarks': "Good work!"}
            )
        print("Seeded grades for Quiz 1.")

if __name__ == "__main__":
    # You can specify the schema here
    seed_data('school_a')
