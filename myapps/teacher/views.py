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
    context = {
        'total_classes': classes.count(),
        'recent_assignments': Assignment.objects.filter(class_subject__teacher=request.user).order_by('-created_at')[:5],
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def teacher_classes(request):
    if not teacher_check(request.user):
        return redirect('login')
    
    classes = ClassSubject.objects.filter(teacher=request.user)
    return render(request, 'teacher_classes.html', {'classes': classes})

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
            
            # Validate inputs
            if not student_id or not assignment_id:
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            # Get the assignment and verify teacher owns it
            assignment = get_object_or_404(Assignment, id=assignment_id, class_subject__teacher=request.user)
            
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
