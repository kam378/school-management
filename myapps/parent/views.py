from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import ParentProfile
from .forms import ParentUserForm, ParentAddressForm
from myapps.school_admin.models import Announcement, CalendarEvent
from myapps.school_admin.utils import get_notifications
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def parent_dashboard(request):
    if request.user.role != 'parent':
        return redirect('login')
    
    from myapps.teacher.models import Grade
    from myapps.attendances.models import StudentAttendance
    from myapps.school_admin.models import Classroom
    from django.db.models import Avg, Sum
    
    profile, created = ParentProfile.objects.get_or_create(parent=request.user)
    children_objs = profile.children.all()
    
    children_data = []
    for student in children_objs:
        # Calculate GPA (Average Percentage)
        grades = Grade.objects.filter(student=student)
        avg_grade = 0
        if grades.exists():
            total_score = grades.aggregate(Sum('score'))['score__sum'] or 0
            total_max = grades.aggregate(Sum('assignment__max_score'))['assignment__max_score__sum'] or 1
            avg_grade = round((total_score / total_max) * 100, 1)
        
        # Calculate Attendance %
        attendance = StudentAttendance.objects.filter(student=student)
        total_days = attendance.count()
        present_days = attendance.filter(status='present').count()
        late_days = attendance.filter(status='late').count()
        
        att_rate = 0
        if total_days > 0:
            # Late counts as 0.5 present
            att_rate = round(((present_days + (late_days * 0.5)) / total_days) * 100, 1)
        
        # Get Classroom
        classroom = Classroom.objects.filter(students=student).first()
        
        children_data.append({
            'obj': student,
            'avg_grade': avg_grade,
            'att_rate': att_rate,
            'classroom': classroom
        })
    
    announcements = Announcement.objects.all().order_by('-date')[:5]
    
    return render(request, 'parent_dashboard.html', {
        'profile': profile,
        'children_data': children_data,
        'announcements': announcements,
        'user_notification_count': get_notifications(request.user)
    })

@login_required
def parent_announcements(request):
    if request.user.role != 'parent':
        return redirect('login')
    
    announcements = Announcement.objects.all().order_by('-date')
    return render(request, 'parent_announcements.html', {
        'announcements': announcements,
        'user_notification_count': get_notifications(request.user)
    })

@login_required
def parent_child_results(request, student_id):
    if request.user.role != 'parent':
        return redirect('login')
    
    from myapps.teacher.models import Grade
    from myapps.attendances.models import StudentAttendance
    from myapps.school_admin.models import Classroom, Subject, ClassSubject
    from django.db.models import Avg, Sum
    
    student = get_object_or_404(User, id=student_id, role='student')
    profile = get_object_or_404(ParentProfile, parent=request.user)
    
    if student not in profile.children.all():
        return redirect('parent_dashboard')
    
    # 1. Performance Overview
    grades = Grade.objects.filter(student=student)
    avg_grade_pct = 0
    if grades.exists():
        total_score = grades.aggregate(Sum('score'))['score__sum'] or 0
        total_max = grades.aggregate(Sum('assignment__max_score'))['assignment__max_score__sum'] or 1
        avg_grade_pct = (total_score / total_max) * 100
    
    # Simple Grade Mapping
    def get_grade_letter(pct):
        if pct >= 90: return 'A+'
        if pct >= 80: return 'A'
        if pct >= 70: return 'B'
        if pct >= 60: return 'C'
        if pct >= 50: return 'D'
        return 'F'
    
    display_grade = get_grade_letter(avg_grade_pct)

    # 2. Attendance Summary
    attendance = StudentAttendance.objects.filter(student=student)
    total_days = attendance.count()
    att_rate = 0
    if total_days > 0:
        present = attendance.filter(status='present').count()
        late = attendance.filter(status='late').count()
        att_rate = round(((present + (late * 0.5)) / total_days) * 100, 1)

    # 3. Class Rank (Simplified: Based on total scores in the same classroom)
    classroom = Classroom.objects.filter(students=student).first()
    rank_str = "N/A"
    if classroom:
        all_students = classroom.students.all()
        student_performances = []
        for s in all_students:
            s_grades = Grade.objects.filter(student=s)
            s_total = s_grades.aggregate(Sum('score'))['score__sum'] or 0
            student_performances.append((s.id, s_total))
        
        # Sort by total score descending
        student_performances.sort(key=lambda x: x[1], reverse=True)
        
        # Find current student index
        try:
            rank = [x[0] for x in student_performances].index(student.id) + 1
            rank_str = f"{rank} / {all_students.count()}"
        except ValueError:
            pass

    # 4. Subject Wise Data
    # Get all subjects the student is taking via their classroom
    subject_wise = []
    if classroom:
        class_subjects = ClassSubject.objects.filter(classroom=classroom)
        for cs in class_subjects:
            subj_grades = Grade.objects.filter(student=student, assignment__class_subject=cs)
            if subj_grades.exists():
                s_total = subj_grades.aggregate(Sum('score'))['score__sum'] or 0
                s_max = subj_grades.aggregate(Sum('assignment__max_score'))['assignment__max_score__sum'] or 1
                subj_pct = (s_total / s_max) * 100
                subject_wise.append({
                    'name': cs.subject.name,
                    'total': f"{s_total}/{s_max}",
                    'pct': round(subj_pct, 1),
                    'grade': get_grade_letter(subj_pct)
                })

    # 5. Latest Feedback
    latest_grade = grades.order_by('-graded_at').first()

    return render(request, 'parent_child_results.html', {
        'student': student,
        'avg_grade': display_grade,
        'att_rate': att_rate,
        'rank': rank_str,
        'subject_wise': subject_wise,
        'latest_grade': latest_grade,
        'user_notification_count': get_notifications(request.user)
    })

@login_required
def parent_profile(request):
    if request.user.role != 'parent':
        return redirect('login')
    
    profile, created = ParentProfile.objects.get_or_create(parent=request.user)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = ParentUserForm(request.POST, instance=request.user)
            address_form = ParentAddressForm(request.POST, instance=profile)
            password_form = PasswordChangeForm(request.user)
            
            if user_form.is_valid() and address_form.is_valid():
                user_form.save()
                address_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('parent_profile')
        
        elif 'change_password' in request.POST:
            user_form = ParentUserForm(instance=request.user)
            address_form = ParentAddressForm(instance=profile)
            password_form = PasswordChangeForm(request.user, request.POST)
            
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('parent_profile')
    else:
        user_form = ParentUserForm(instance=request.user)
        address_form = ParentAddressForm(instance=profile)
        password_form = PasswordChangeForm(request.user)
    
    user_notifications_count = get_notifications(request.user)
    
    return render(request, 'parent_profile.html', {
        'user_form': user_form,
        'address_form': address_form,
        'password_form': password_form,
        'profile': profile,
        'user_notification_count': user_notifications_count
    })
