from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from myapps.school_admin.models import ClassSubject, Classroom, Subject
from .models import Assignment, Grade
from .forms import AssignmentForm, TeacherProfileForm


def teacher_check(user):
    return user.is_authenticated and user.role == 'teacher'

@login_required
def teacher_dashboard(request):
    if not teacher_check(request.user):
        return redirect('login')
    
    classes = ClassSubject.objects.filter(teacher=request.user)
    
    # Check if teacher is a homeroom teacher
    homeroom_class = Classroom.objects.filter(homeroom_teacher=request.user).first()
    
    context = {
        'total_classes': classes.count(),
        'recent_assignments': Assignment.objects.filter(class_subject__teacher=request.user).order_by('-created_at')[:5],
        'homeroom_class': homeroom_class,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def teacher_classes(request):
    if not teacher_check(request.user):
        return redirect('login')
    
    classes = ClassSubject.objects.filter(teacher=request.user)
    return render(request, 'teacher_classes.html', {'classes': classes})

@login_required
def teacher_homeroom_class(request):
    """View for homeroom class roster with quick access to student details"""
    if not teacher_check(request.user):
        return redirect('login')
    
    homeroom_class = get_object_or_404(Classroom, homeroom_teacher=request.user)
    students = homeroom_class.students.all().order_by('first_name', 'last_name')
    
    # Get attendance stats for each student
    from myapps.attendances.models import StudentAttendance
    from myapps.school_admin.models import Term
    active_term = Term.objects.filter(is_active=True).first()
    
    student_data = []
    for student in students:
        attendance_qs = StudentAttendance.objects.filter(student=student)
        if active_term:
            attendance_qs = attendance_qs.filter(term=active_term)
            
        total_days = attendance_qs.count()
        present_days = attendance_qs.filter(status='present').count()
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        
        student_data.append({
            'student': student,
            'attendance_rate': round(attendance_rate, 1),
            'total_days': total_days
        })
    
    context = {
        'homeroom_class': homeroom_class,
        'student_data': student_data,
    }
    return render(request, 'teacher_homeroom_class.html', context)

@login_required
def gradebook_view(request, class_subject_id):
    if not teacher_check(request.user):
        return redirect('login')
    
    class_subject = get_object_or_404(ClassSubject, id=class_subject_id, teacher=request.user)
    students = class_subject.classroom.students.all().order_by('first_name', 'last_name')
    assignments = class_subject.assignments.all().order_by('due_date')
    
    # Building a matrix: Student -> {AssignmentID -> Score}
    grade_matrix = {}
    for student in students:
        student_grades = {}
        for assignment in assignments:
            grade = Grade.objects.filter(student=student, assignment=assignment).first()
            student_grades[assignment.id] = grade.score if grade else '-'
        grade_matrix[student.id] = student_grades

    context = {
        'class_subject': class_subject,
        'students': students,
        'assignments': assignments,
        'grade_matrix': grade_matrix,
        'enable_attendance': True, # Default to True, but should fetch from settings
    }
    
    # Check global settings
    from myapps.school_admin.models import SchoolSettings
    settings = SchoolSettings.objects.first()
    if settings:
        context['enable_attendance'] = settings.enable_attendance
        
    return render(request, 'teacher_gradebook.html', context)

@login_required
def teacher_assignments(request):
    if not teacher_check(request.user):
        return redirect('login')
    
    assignments = Assignment.objects.filter(class_subject__teacher=request.user).order_by('-due_date')
    return render(request, 'teacher_assignments.html', {'assignments': assignments})

@login_required
def teacher_add_assignment(request):
    if not teacher_check(request.user):
        return redirect('login')
    
    from myapps.school_admin.models import Term
    active_term = Term.objects.filter(is_active=True).first()
    
    if not active_term:
        messages.error(request, "No active academic term found. Please contact the administrator.")
        return redirect('teacher_assignments')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, teacher=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment created successfully!")
            return redirect('teacher_assignments')
    else:
        form = AssignmentForm(teacher=request.user)
    
    return render(request, 'teacher_assignment_form.html', {'form': form})


@login_required
def enter_grade(request):
    """AJAX endpoint for entering/updating grades"""
    if not teacher_check(request.user):
        return redirect('login')
    
    if request.method == 'POST':
        import json
        from django.http import JsonResponse
        
        try:
            student_id = request.POST.get('student_id')
            assignment_id = request.POST.get('assignment_id')
            score = request.POST.get('score', '').strip()
            
            if not student_id or not assignment_id:
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            from myapps.school_admin.models import Term
            if not Term.objects.filter(is_active=True).exists():
                return JsonResponse({'success': False, 'error': 'Cannot grade: No active term found.'})
            
            # Get the assignment and verify teacher owns it
            assignment = get_object_or_404(Assignment, id=assignment_id, class_subject__teacher=request.user)
            
            # Verify student belongs to the class
            if not assignment.class_subject.classroom.students.filter(id=student_id).exists():
                return JsonResponse({'success': False, 'error': 'Student not found in this class'})
            
            # Handle empty score (delete grade)
            if score == '' or score == '-':
                Grade.objects.filter(student_id=student_id, assignment=assignment).delete()
                return JsonResponse({'success': True, 'score': '-'})
            
            # Validate score is a number and within range
            try:
                score_value = float(score)
                if score_value < 0 or score_value > assignment.max_score:
                    return JsonResponse({
                        'success': False, 
                        'error': f'Score must be between 0 and {assignment.max_score}'
                    })
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid score format'})
            
            # Create or update grade
            grade, created = Grade.objects.update_or_create(
                student_id=student_id,
                assignment=assignment,
                defaults={'score': score_value}
            )
            
            return JsonResponse({
                'success': True, 
                'score': score_value,
                'action': 'created' if created else 'updated'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def teacher_edit_assignment(request, assignment_id):
    """Edit an existing assignment"""
    if not teacher_check(request.user):
        return redirect('login')
    
    # Get assignment and verify teacher owns it
    assignment = get_object_or_404(Assignment, id=assignment_id, class_subject__teacher=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment, teacher=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect('teacher_assignments')
    else:
        form = AssignmentForm(instance=assignment, teacher=request.user)
    
    return render(request, 'teacher_assignment_form.html', {
        'form': form,
        'assignment': assignment,
        'is_edit': True
    })


@login_required
def teacher_delete_assignment(request, assignment_id):
    """Delete an assignment"""
    if not teacher_check(request.user):
        return redirect('login')
    
    # Get assignment and verify teacher owns it
    assignment = get_object_or_404(Assignment, id=assignment_id, class_subject__teacher=request.user)
    
    if request.method == 'POST':
        assignment_title = assignment.title
        assignment.delete()
        messages.success(request, f'Assignment "{assignment_title}" deleted successfully!')
        return redirect('teacher_assignments')
    
    return render(request, 'teacher_assignment_confirm_delete.html', {'assignment': assignment})
@login_required
def teacher_timetable(request):
    if not teacher_check(request.user):
        return redirect('login')
    
    from myapps.school_admin.models import Timetable
    timetable_data = {}
    days = Timetable.DAYS_OF_WEEK

    # Get slots for all classes this teacher is assigned to
    slots = Timetable.objects.filter(class_subject__teacher=request.user).order_by('start_time')
    
    timetable_data = {day[0]: [] for day in days}
    for slot in slots:
        timetable_data[slot.day].append(slot)

    return render(request, "teacher_timetable.html", {
        'timetable_data': timetable_data,
        'days': days
    })


@login_required
def teacher_profile(request):
    if not teacher_check(request.user):
        return redirect('login')

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = TeacherProfileForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('teacher_profile')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            profile_form = TeacherProfileForm(instance=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('teacher_profile')
    else:
        profile_form = TeacherProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    return render(request, 'teacher_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })

@login_required
def teacher_assignment_detail(request, assignment_id):
    """View details of an assignment and student submissions"""
    if not teacher_check(request.user):
        return redirect('login')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, class_subject__teacher=request.user)
    submissions = assignment.submissions.all().select_related('student')
    
    # Get all students in the class to check for missing submissions
    all_students = assignment.class_subject.classroom.students.all().order_by('first_name', 'last_name')
    
    # Map submissions by student ID for easy lookup
    submission_map = {sub.student.id: sub for sub in submissions}
    
    student_status = []
    for student in all_students:
        submission = submission_map.get(student.id)
        # Get grade if exists
        grade = Grade.objects.filter(assignment=assignment, student=student).first()
        
        student_status.append({
            'student': student,
            'submission': submission,
            'grade': grade,
            'status': 'Submitted' if submission else 'Pending'
        })

    return render(request, 'teacher_assignment_detail.html', {
        'assignment': assignment,
        'student_status': student_status
    })

@login_required
def teacher_student_detail(request, student_id):
    """
    View student details with permission-based access:
    - Homeroom teachers: Full academic history + attendance
    - Regular teachers: Only grades for subjects they teach
    """
    if not teacher_check(request.user):
        return redirect('login')
    
    from myapps.accounts.models import User
    from myapps.attendances.models import StudentAttendance
    from django.db.models import Count, Q
    
    student = get_object_or_404(User, id=student_id, role='student')
    
    # Check if teacher is the homeroom teacher
    is_homeroom_teacher = Classroom.objects.filter(
        students=student,
        homeroom_teacher=request.user
    ).exists()
    
    # Check if teacher teaches this student in any subject
    teaches_student = ClassSubject.objects.filter(
        teacher=request.user,
        classroom__students=student
    ).exists()
    
    if not is_homeroom_teacher and not teaches_student:
        messages.error(request, "You don't have permission to view this student's details.")
        return redirect('teacher_dashboard')
    
    # Get student's classroom
    classroom = Classroom.objects.filter(students=student).first()
    
    # Attendance data (only for homeroom teachers)
    attendance_data = None
    if is_homeroom_teacher:
        total_days = StudentAttendance.objects.filter(student=student).count()
        present_days = StudentAttendance.objects.filter(student=student, status='present').count()
        attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
        recent_attendance = StudentAttendance.objects.filter(student=student).order_by('-date')[:10]
        
        attendance_data = {
            'total_days': total_days,
            'present_days': present_days,
            'attendance_rate': round(attendance_rate, 1),
            'recent_records': recent_attendance
        }
    
    # Grade data (filtered by permission)
    if is_homeroom_teacher:
        # Homeroom teacher sees ALL subjects
        all_grades = Grade.objects.filter(student=student).select_related('assignment__class_subject__subject')
    else:
        # Regular teacher sees only their subjects
        teacher_subjects = ClassSubject.objects.filter(teacher=request.user, classroom__students=student)
        all_grades = Grade.objects.filter(
            student=student,
            assignment__class_subject__in=teacher_subjects
        ).select_related('assignment__class_subject__subject')
    
    # Group grades by subject
    grades_by_subject = {}
    for grade in all_grades:
        subject_name = grade.assignment.class_subject.subject.name
        if subject_name not in grades_by_subject:
            grades_by_subject[subject_name] = []
        grades_by_subject[subject_name].append({
            'assignment': grade.assignment.title,
            'score': grade.score,
            'max_score': grade.assignment.max_score,
            'percentage': round((grade.score / grade.assignment.max_score * 100), 1) if grade.assignment.max_score > 0 else 0,
            'graded_at': grade.graded_at
        })
    
    context = {
        'student': student,
        'classroom': classroom,
        'is_homeroom_teacher': is_homeroom_teacher,
        'attendance_data': attendance_data,
        'grades_by_subject': grades_by_subject,
    }
    
    return render(request, 'teacher_student_detail.html', context)
