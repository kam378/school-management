from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # Used for error/validation messages; success notifications use Notification model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from myapps.core.models import Notification

from myapps.school_admin.models import (
    Announcement, SchoolSettings, GradeLevel, Subject, Classroom, 
    ClassSubject, Timetable, CalendarEvent
)
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, AnnouncementForm, 
    SchoolSettingsForm, GradeLevelForm, SubjectForm, ClassroomForm, 
    ClassSubjectForm, TimetableForm, AdminSetPasswordForm, CalendarEventForm, AdminProfileForm
)
from .utils import get_notifications
from myapps.super_admin.utils import QuotaManager
from django.utils import timezone
from django.db import connection, transaction
from myapps.attendances.models import StudentAttendance

User = get_user_model()


# Create your views here.
def admin_dashboard(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  user_notifications_count = get_notifications(request.user)
  
  num_students = User.objects.filter(role='student').count()
  num_teachers = User.objects.filter(role='teacher').count()
  num_parents = User.objects.filter(role='parent').count()
  num_admins = User.objects.filter(role='school_admin').count()
  
  context = {
      'num_students': num_students,
      'num_teachers': num_teachers,
      'num_parents': num_parents,
      'num_admins': num_admins,
      'user_notification_count' : user_notifications_count,
  }  
  
  return render(request, 'admin_dashboard.html', context)
@login_required # I should check if login_required is imported, it is not in the view snippet. Let me check the top of the file.
def admin_delete_user(request, id):
    if not request.user.role == "school_admin":
        return redirect("login")
    
    user_to_delete = get_object_or_404(User, custom_id=id)
    
    # Can't delete yourself
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("school_admin_manage_users")
        
    username = user_to_delete.username
    user_to_delete.delete()
    
    messages.success(request, f"User {username} has been deleted.")
    Notification.objects.create(
        user=request.user,
        title="User Deleted",
        body=f"You have successfully deleted user {username}.",
    )
    return redirect("school_admin_manage_users")

@login_required
def admin_reset_password(request, user_id):
    if request.user.role != 'school_admin':
        return redirect('login')
    
    user_to_reset = get_object_or_404(User, custom_id=user_id)
    
    if request.method == 'POST':
        form = AdminSetPasswordForm(user_to_reset, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Password for {user_to_reset.username} has been reset.')
            return redirect('school_admin_manage_users')
    else:
        form = AdminSetPasswordForm(user_to_reset)
    
    user_notifications_count = get_notifications(request.user)
    return render(request, 'admin_reset_password.html', {
        'form': form,
        'target_user': user_to_reset,
        'user_notification_count': user_notifications_count
    })

def admin_manage_users(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  user_notifications_count = get_notifications(request.user)
  
  # Start with all users
  users = User.objects.all()
  
  # Handle search query
  search_query = request.GET.get('search', '').strip()
  if search_query:
      users = users.filter(
          Q(username__icontains=search_query) |
          Q(first_name__icontains=search_query) |
          Q(last_name__icontains=search_query) |
          Q(email__icontains=search_query) |
          Q(custom_id__icontains=search_query)
      )
  
  # Handle role filter
  role_filter = request.GET.get('role', '').strip()
  if role_filter:
      users = users.filter(role=role_filter)
  
  context = {
      'users': users,
      'user_notification_count' : user_notifications_count,
      'search_query': search_query,
      'role_filter': role_filter,
  }
  return render(request, 'admin_manage_users.html', context)
@login_required 
def admin_edit_user(request, id):
    if not request.user.role == "school_admin":
        return redirect("login")
    
    user_to_edit = get_object_or_404(User, custom_id=id)
    profile_form = None
    
    # Init Profile Form if student or parent
    if user_to_edit.role == 'student':
        # Ensure profile exists
        from myapps.student.models import StudentProfile
        from .forms import StudentProfileAdminForm 
        profile, created = StudentProfile.objects.get_or_create(student=user_to_edit)
        profile_form = StudentProfileAdminForm(instance=profile)
    elif user_to_edit.role == 'parent':
        from myapps.parent.models import ParentProfile
        from .forms import ParentProfileAdminForm
        profile, created = ParentProfile.objects.get_or_create(parent=user_to_edit)
        profile_form = ParentProfileAdminForm(instance=profile)

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user_to_edit)
        
        # Determine if profile info is being saved
        if user_to_edit.role == 'student':
            from .forms import StudentProfileAdminForm
            profile, created = StudentProfile.objects.get_or_create(student=user_to_edit)
            profile_form = StudentProfileAdminForm(request.POST, instance=profile)
        elif user_to_edit.role == 'parent':
            from .forms import ParentProfileAdminForm
            profile, created = ParentProfile.objects.get_or_create(parent=user_to_edit)
            profile_form = ParentProfileAdminForm(request.POST, instance=profile)

        if form.is_valid():
            if profile_form:
                if profile_form.is_valid():
                    profile_form.save()
                else:
                     # Return with errors
                     status_choices = [c[0] for c in User.ROLE_CHOICES]
                     return render(request, 'admin_edit_user.html', {
                        'form': form, 
                        'user_to_edit': user_to_edit,
                        'profile_form': profile_form,
                        'status_choices': status_choices,
                        'user_notification_count': get_notifications(request.user)
                     })

            user = form.save()
            messages.success(request, f"User {user.username} updated successfully.")
            return redirect("school_admin_manage_users")
    else:
        form = CustomUserChangeForm(instance=user_to_edit)
    
    status_choices = [c[0] for c in User.ROLE_CHOICES]
    
    context = {
        'status_choices' : status_choices,
        'user_to_edit' : user_to_edit,
        'active' : user_to_edit.is_active,
        'form': form,
        'profile_form': profile_form,
        'user_notification_count' : get_notifications(request.user),
    }

    return render(request, 'admin_edit_user.html', context)
def admin_add_user(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")
  
  if request.method == "POST":
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
        role = form.cleaned_data.get('role')
        tenant = connection.tenant
        
        if role == 'student' and not QuotaManager.can_add_student(tenant):
            messages.error(request, "Enrollment failed: Student quota exceeded for your current plan. Please contact the administrator.")
            return redirect("school_admin_add_user")
            
        if role == 'teacher' and not QuotaManager.can_add_teacher(tenant):
            messages.error(request, "Hire failed: Teacher quota exceeded for your current plan. Please contact the administrator.")
            return redirect("school_admin_add_user")

        user = form.save()
        messages.success(request, f"Successfully created user {user.username} with ID {user.custom_id}")
        
        Notification.objects.create(
            user=request.user,
            title="User Added Successfully",
            body=f"\n\n        You have Successfully added user {user.username}\n\n      ",
        )
        return redirect("school_admin_manage_users")

    else:
        # If form is invalid, errors are stored in form.errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
  else:
    form = CustomUserCreationForm()

  user_notifications_count = get_notifications(request.user)
  
  status_choices = [c[0] for c in User.ROLE_CHOICES]
  context = {
    'status_choices' : status_choices,
    'form': form, # Pass form to template if needed/upgraded later
    'user_notification_count' : user_notifications_count,
  }
  return render(request, "admin_add_user.html", context)

def admin_announcements(request):

  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  announcements = Announcement.objects.all().order_by("-date")
  user_notifications_count = get_notifications(request.user)

  context = {
    "announcements" : announcements,
    'user_notification_count' : user_notifications_count,
  }

  

  return render(request, "admin_announcements.html", context)

def admin_add_announcements(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")
  if request.method == "POST":
    form = AnnouncementForm(request.POST)
    if form.is_valid():
        announcement = form.save()
        
        Notification.objects.create(
            user=request.user,
            title="New Notification Added successfully",
            body=f"\n\n        You have Successfully added A new Announcement {announcement.title}\n\n      ",
        )
        return redirect("school_admin_announcements")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
  else:
    form = AnnouncementForm()

  user_notifications_count = get_notifications(request.user)

  context = {
    'user_notification_count' : user_notifications_count,
    'form' : form,
  }

  return render(request, "admin_add_announcements.html", context)

def admin_user_notifications(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  notifications = Notification.objects.filter(user=request.user, is_read=False).order_by("-date")
  user_notifications_count = get_notifications(request.user)

  context ={
    "notifications" : notifications,
    'user_notification_count' : user_notifications_count,
  }

  return render(request, "admin_notifications.html", context)

def admin_single_announcement(request, id, title):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  announcement = Announcement.objects.get(id = id, title = title)
  user_notifications_count = get_notifications(request.user)


  context = {
    "announcement" : announcement,
    'user_notification_count' : user_notifications_count,
  }


  return render(request, "admin_single_announcements.html", context)

def admin_edit_announcement(request, id):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")
  
  announcement = get_object_or_404(Announcement, id=id)
  
  if request.method == "POST":
    form = AnnouncementForm(request.POST, instance=announcement)
    if form.is_valid():
      form.save()
      
      Notification.objects.create(
        user=request.user,
        title="Announcement Updated",
        body=f"\n\n        You have successfully updated the announcement: {announcement.title}\n\n      ",
      )
      
      return redirect("school_admin_announcements")
    else:
      for field, errors in form.errors.items():
        for error in errors:
          messages.error(request, f"{field}: {error}")
  else:
    form = AnnouncementForm(instance=announcement)
  
  user_notifications_count = get_notifications(request.user)
  
  context = {
    "announcement": announcement,
    "form": form,
    'user_notification_count': user_notifications_count,
  }
  
  return render(request, "admin_edit_announcements.html", context)

def admin_delete_announcement(request, id):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  announcement = get_object_or_404(Announcement, id=id)
  announcement.delete()

  Notification.objects.create(
      user=request.user,
      title="Announcement Deleted",
      body=f"\n\n        You deleted an Announcement {announcement.title}\n\n      ",
  )

  return redirect("school_admin_announcements")

def admin_single_notification(request, id):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  notification = Notification.objects.get(id = id)
  print(notification.is_read)
  notification.is_read = True
  notification.save()

  user_notifications_count = get_notifications(request.user)
  
  context = {
    "notification" : notification,
    'user_notification_count' : user_notifications_count,
  }

  return render(request, "admin_single_notification.html", context)

def admin_analytics(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  user_notifications_count = get_notifications(request.user)

  # Fetch real data for analytics
  num_students = User.objects.filter(role='student').count()
  num_teachers = User.objects.filter(role='teacher').count()
  num_parents = User.objects.filter(role='parent').count()
  
  # Mock data for demonstration (replace with real models later)
  total_revenue = 15400 # Mock
  attendance_rate = 92 # Mock percentage

  context = {
      'num_students': num_students,
      'num_teachers': num_teachers,
      'num_parents': num_parents,
      'total_revenue': total_revenue,
      'attendance_rate': attendance_rate,
      'user_notification_count': user_notifications_count,
  }
  return render(request, "admin_analytics.html", context)

def admin_settings(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "school_admin":
    return redirect("login")

  # Get or create the singleton settings object
  settings_obj = SchoolSettings.objects.first()
  if not settings_obj:
      settings_obj = SchoolSettings.objects.create()

  if request.method == "POST":
      form = SchoolSettingsForm(request.POST, instance=settings_obj)
      if form.is_valid():
          form.save()
          messages.success(request, "Settings updated successfully!")
          Notification.objects.create(
              user=request.user,
              title="Settings Updated",
              body="You have successfully updated the global school settings.",
              is_read=False
          )
          return redirect("school_admin_settings")
      else:
          messages.error(request, "Please correct the errors below.")
  else:
      form = SchoolSettingsForm(instance=settings_obj)

  user_notifications_count = get_notifications(request.user)

  context = {
      'form': form,
      'settings': settings_obj,
      'user_notification_count': user_notifications_count,
  }
  return render(request, "admin_settings.html", context)

# --- Academic Management ---

def admin_academic_overview(request):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")
    
    context = {
        'grade_levels_count': GradeLevel.objects.count(),
        'subjects_count': Subject.objects.count(),
        'classrooms_count': Classroom.objects.count(),
        'user_notification_count': get_notifications(request.user),
    }
    return render(request, 'admin_academic_overview.html', context)

# Grade Levels
def admin_manage_grade_levels(request):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")
    
    levels = GradeLevel.objects.all()
    if request.method == "POST":
        form = GradeLevelForm(request.POST)
        if form.is_valid():
            level = form.save()
            Notification.objects.create(
                user=request.user,
                title="Grade Level Added",
                body=f"Successfully created grade level '{level.name}'."
            )
            return redirect("admin_manage_grade_levels")
    else:
        form = GradeLevelForm()
        
    return render(request, 'admin_manage_grade_levels.html', {
        'levels': levels, 
        'form': form,
        'user_notification_count': get_notifications(request.user)
    })

# Subjects
def admin_manage_subjects(request):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")
    
    subjects = Subject.objects.all()
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            Notification.objects.create(
                user=request.user,
                title="Subject Added",
                body=f"Successfully created subject '{subject.name}'."
            )
            return redirect("admin_manage_subjects")
    else:
        form = SubjectForm()
        
    return render(request, 'admin_manage_subjects.html', {
        'subjects': subjects, 
        'form': form,
        'user_notification_count': get_notifications(request.user)
    })

# Classrooms
def admin_manage_classrooms(request):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")
    
    classrooms = Classroom.objects.all()
    if request.method == "POST":
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            Notification.objects.create(
                user=request.user,
                title="Classroom Created",
                body=f"Successfully created classroom '{classroom.name}' for {classroom.level.name}."
            )
            return redirect("admin_manage_classrooms")
    else:
        form = ClassroomForm()
        
    return render(request, 'admin_manage_classrooms.html', {
        'classrooms': classrooms, 
        'form': form,
        'user_notification_count': get_notifications(request.user)
    })

# Timetable
def admin_manage_timetable(request, classroom_id=None):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")
    
    classrooms = Classroom.objects.all()
    selected_classroom = None
    timetable_data = None
    
    if classroom_id:
        selected_classroom = get_object_or_404(Classroom, id=classroom_id)
        # Fetch slots and organize by day
        slots = Timetable.objects.filter(class_subject__classroom=selected_classroom)
        timetable_data = {day[0]: [] for day in Timetable.DAYS_OF_WEEK}
        for slot in slots:
            timetable_data[slot.day].append(slot)

    if request.method == "POST":
        form = TimetableForm(request.POST)
        if form.is_valid():
            slot = form.save()
            Notification.objects.create(
                user=request.user,
                title="Timetable Slot Added",
                body=f"Added {slot.class_subject.subject.name} schedule for {slot.get_day_display()} at {slot.start_time}."
            )
            return redirect("admin_manage_timetable", classroom_id=classroom_id) if classroom_id else redirect("admin_manage_timetable")
    else:
        form = TimetableForm()

    return render(request, 'admin_manage_timetable.html', {
        'classrooms': classrooms,
        'selected_classroom': selected_classroom,
        'timetable_data': timetable_data,
        'form': form,
        'days': Timetable.DAYS_OF_WEEK,
    })

def admin_delete_timetable_slot(request, slot_id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")

    
    slot = get_object_or_404(Timetable, id=slot_id)
    classroom_id = slot.class_subject.classroom.id
    slot_info = f"{slot.class_subject.subject.name} on {slot.get_day_display()}"
    slot.delete()
    Notification.objects.create(
        user=request.user,
        title="Timetable Slot Removed",
        body=f"Deleted schedule slot: {slot_info}."
    )
    return redirect("admin_manage_timetable", classroom_id=classroom_id)


# Class Subject (Assigning Teachers)
def admin_manage_class_subjects(request):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")
    
    assignments = ClassSubject.objects.all()
    classroom_id = request.GET.get('classroom') or request.POST.get('classroom')
    
    if request.method == "POST":
        form = ClassSubjectForm(request.POST, classroom_id=classroom_id)
        if form.is_valid():
            # Check if this is just a classroom change (triggered by JS) or a final submit
            if 'save_assignment' in request.POST:
                assignment = form.save()
                Notification.objects.create(
                    user=request.user,
                    title="Teacher Assigned",
                    body=f"Assigned {assignment.teacher.get_full_name()} to teach {assignment.subject.name} in {assignment.classroom.name}."
                )
                return redirect("admin_manage_class_subjects")
            else:
                # Just a classroom change, return form with filtered subjects
                pass
    else:
        form = ClassSubjectForm(classroom_id=classroom_id)
        
    return render(request, 'admin_manage_class_subjects.html', {
        'assignments': assignments,
        'form': form,
        'user_notification_count': get_notifications(request.user)
    })

# CRUD for Grades, Subjects, Classrooms
def admin_edit_grade_level(request, id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")

    level = get_object_or_404(GradeLevel, id=id)
    if request.method == "POST":
        form = GradeLevelForm(request.POST, instance=level)
        if form.is_valid():
            level = form.save()
            Notification.objects.create(
                user=request.user,
                title="Grade Level Updated",
                body=f"Successfully updated grade level '{level.name}'."
            )
            return redirect("admin_manage_grade_levels")
    else:
        form = GradeLevelForm(instance=level)
    return render(request, 'admin_academic_form.html', {'form': form, 'title': 'Edit Grade Level'})

def admin_delete_grade_level(request, id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")

    level = get_object_or_404(GradeLevel, id=id)
    level_name = level.name
    level.delete()
    Notification.objects.create(
        user=request.user,
        title="Grade Level Deleted",
        body=f"Removed grade level '{level_name}' from the system."
    )
    return redirect("admin_manage_grade_levels")

def admin_edit_subject(request, id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")

    subject = get_object_or_404(Subject, id=id)
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            Notification.objects.create(
                user=request.user,
                title="Subject Updated",
                body=f"Successfully updated subject '{subject.name}'."
            )
            return redirect("admin_manage_subjects")
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'admin_academic_form.html', {'form': form, 'title': 'Edit Subject'})

def admin_delete_subject(request, id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")

    subject = get_object_or_404(Subject, id=id)
    subject_name = subject.name
    subject.delete()
    Notification.objects.create(
        user=request.user,
        title="Subject Deleted",
        body=f"Removed subject '{subject_name}' from curriculum."
    )
    return redirect("admin_manage_subjects")

def admin_edit_classroom(request, id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")

    classroom = get_object_or_404(Classroom, id=id)
    if request.method == "POST":
        form = ClassroomForm(request.POST, instance=classroom)
        if form.is_valid():
            classroom = form.save()
            Notification.objects.create(
                user=request.user,
                title="Classroom Updated",
                body=f"Successfully updated classroom '{classroom.name}'."
            )
            return redirect("admin_manage_classrooms")
    else:
        form = ClassroomForm(instance=classroom)
    return render(request, 'admin_academic_form.html', {'form': form, 'title': 'Edit Classroom'})

def admin_delete_classroom(request, id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")

    classroom = get_object_or_404(Classroom, id=id)
    classroom_name = classroom.name
    classroom.delete()
    Notification.objects.create(
        user=request.user,
        title="Classroom Deleted",
        body=f"Removed classroom '{classroom_name}' from the system."
    )
    return redirect("admin_manage_classrooms")

def admin_delete_class_subject(request, id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")

    assignment = get_object_or_404(ClassSubject, id=id)
    assignment_info = f"{assignment.teacher.get_full_name()} - {assignment.subject.name}"
    assignment.delete()
    Notification.objects.create(
        user=request.user,
        title="Teacher Assignment Removed",
        body=f"Removed assignment: {assignment_info}."
    )
    return redirect("admin_manage_class_subjects")


def admin_delete_timetable_slot(request, slot_id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect('login')
        
    slot = get_object_or_404(Timetable, id=slot_id)
    classroom_id = slot.class_subject.classroom.id
    slot.delete()
    Notification.objects.create(
        user=request.user,
        message="Timetable slot deleted successfully",
        notification_type='success'
    )
    return redirect('admin_manage_timetable', classroom_id=classroom_id)


# Student Promotion & Year-End Rollover
from myapps.student.models import StudentProfile
from .models import PromotionRecord 

@login_required
def admin_student_promotion(request):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect('login')
    
    # Ensure all student users have a profile
    student_users = User.objects.filter(role='student')
    
    # Pre-fetch all profiles with related data for efficiency
    # We do a sync pass first: if a profile has a classroom but no grade_level, set it.
    
    for student in student_users:
        profile, created = StudentProfile.objects.get_or_create(student=student)
        
        # Self-healing: If connected to a classroom but missing grade_level, sync it.
        if profile.classroom and not profile.grade_level:
            profile.grade_level = profile.classroom.level
            profile.save()
            
    # Get all grade levels ordered by name
    grade_levels = GradeLevel.objects.all()
    classrooms = Classroom.objects.all()
    
    # Structure data: {grade: [students...]}
    students_by_grade = {}
    
    for grade in grade_levels:
        # Get profiles for this grade, select_related for performance
        profiles = StudentProfile.objects.filter(grade_level=grade).select_related('student', 'classroom')
        students_by_grade[grade] = profiles
        
    # Get students with NO grade level assigned yet
    ungraded_students = StudentProfile.objects.filter(grade_level__isnull=True).select_related('student', 'classroom')
    
    context = {
        'grade_levels': grade_levels,
        'classrooms': classrooms,
        'students_by_grade': students_by_grade,
        'ungraded_students': ungraded_students,
    }
    return render(request, 'admin_student_promotion.html', context)


def admin_promote_execute(request):
    if not request.user.is_authenticated or not request.user.role == "school_admin" or request.method != 'POST':
        return redirect('login')
        
    try:
        selected_student_ids = request.POST.getlist('selected_students')
        target_grade_id = request.POST.get('target_grade')
        target_classroom_id = request.POST.get('target_classroom')
        # academic_year = request.POST.get('academic_year', '2024-2025') 
        # Ideally, we get the current active year from settings, for now we default or let user input elsewhere.
        
        # Get School Settings for Academic Year if possible, otherwise default
        try:
           # Assuming we have logic to get current year, e.g. from SchoolSettings or calculation
           # For now, let's just use a string or current year.
           import datetime
           current_year = datetime.datetime.now().year
           academic_year = f"{current_year}-{current_year+1}"
        except:
            academic_year = "2024-2025"
        
        if not selected_student_ids:
            messages.error(request, "No students selected for promotion.")
            return redirect('admin_student_promotion')
            
        # Handle Graduation / Archiving
        if target_grade_id == 'graduate':
            with transaction.atomic():
                for student_id in selected_student_ids:
                    profile = get_object_or_404(StudentProfile, id=student_id)
                    
                    PromotionRecord.objects.create(
                        student=profile.student,
                        from_grade=profile.grade_level,
                        to_grade=None,
                        from_classroom=profile.classroom,
                        to_classroom=None,
                        promoted_by=request.user,
                        academic_year=academic_year,
                        notes="Student Graduated / Archived"
                    )
                    
                    profile.grade_level = None
                    profile.classroom = None
                    profile.save()
            
            messages.success(request, f"Successfully graduated {len(selected_student_ids)} students.")
            return redirect('admin_student_promotion')

        # Regular Promotion
        target_grade = get_object_or_404(GradeLevel, id=target_grade_id)
        target_classroom = get_object_or_404(Classroom, id=target_classroom_id)
            
        promoted_count = 0
        
        with transaction.atomic():
            for student_id in selected_student_ids:
                # student_id here is the StudentProfile ID
                profile = get_object_or_404(StudentProfile, id=student_id)
                
                # Create Audit Record
                PromotionRecord.objects.create(
                    student=profile.student,
                    from_grade=profile.grade_level,
                    to_grade=target_grade,
                    from_classroom=profile.classroom,
                    to_classroom=target_classroom,
                    promoted_by=request.user,
                    academic_year=academic_year,
                    notes=f"Bulk promotion to {target_grade.name} - {target_classroom.name}"
                )
                
                # Update Profile
                profile.grade_level = target_grade
                profile.classroom = target_classroom
                profile.save()
                
                # Update the User's class subject enrollment? 
                # This depends on how class enrollment works. 
                # If ClassSubjects are tied to Classroom, then just moving the student means they now show up in new class lists.
                
                promoted_count += 1
            
        messages.success(request, f"Successfully promoted {promoted_count} students to {target_grade.name} ({target_classroom.name}).")
        
    except Exception as e:
        messages.error(request, f"Error during promotion: {str(e)}")
        
    return redirect('admin_student_promotion')


def school_calendar(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    events = CalendarEvent.objects.all().order_by('start_date')
    is_admin = request.user.role == "school_admin"
    
    if request.method == "POST":
        if not is_admin:
             messages.error(request, "Only administrators can add events.")
             return redirect("school_calendar")
             
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, "Event added to calendar.")
            return redirect("school_calendar")
    else:
        form = CalendarEventForm() if is_admin else None
        
    # Determine which aside to use
    if request.user.role == "school_admin":
        aside_template = "admin_aside.html"
    elif request.user.role == "teacher":
        aside_template = "teacher_aside.html"
    elif request.user.role == "parent":
        aside_template = "parent_aside.html"
    else:
        aside_template = "student_aside.html"
        
    return render(request, "school_calendar.html", {
        'events': events,
        'form': form,
        'is_admin': is_admin,
        'aside_template': aside_template,
        'user_notification_count': get_notifications(request.user)
    })

def admin_edit_parent_profile(request, custom_id):
    if not request.user.is_authenticated or not request.user.role == "school_admin":
        return redirect("login")
    
    from myapps.parent.models import ParentProfile
    from myapps.parent.forms import ParentProfileForm
    
    user = get_object_or_404(User, custom_id=custom_id, role='parent')
    profile, created = ParentProfile.objects.get_or_create(parent=user)
    
    if request.method == "POST":
        form = ParentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profile for {user.get_full_name()} updated successfully.")
            return redirect('school_admin_manage_users')
    else:
        form = ParentProfileForm(instance=profile)
        
    status_choices = [c[0] for c in User.ROLE_CHOICES]
    
    return render(request, "admin_edit_parent_profile.html", {
        'form': form,
        'edit_user': user,
        'status_choices': status_choices,
        'title': f"Edit Parent Profile: {user.get_full_name()}",
        'user_notification_count': get_notifications(request.user)
    })

def admin_delete_calendar_event(request, id):
    if not request.user.role == 'school_admin':
        return redirect('login')
    event = get_object_or_404(CalendarEvent, id=id)
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('school_calendar')

@login_required
def admin_mark_attendance(request):
    if request.user.role not in ['school_admin', 'teacher']:
        return redirect('login')
    
    selected_classroom_id = request.GET.get('classroom')
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    classrooms = Classroom.objects.all()
    students = []
    
    if selected_classroom_id:
        classroom = get_object_or_404(Classroom, id=selected_classroom_id)
        students = classroom.students.all()
        
        # Prefetch existing attendance for this date
        existing_attendance = StudentAttendance.objects.filter(
            student__in=students, 
            date=selected_date
        )
        att_dict = {a.student_id: a.status for a in existing_attendance}
        
        for s in students:
            s.current_status = att_dict.get(s.id, 'present')

    if request.method == 'POST':
        classroom_id = request.POST.get('classroom_id')
        date = request.POST.get('attendance_date')
        
        # Get all students for this classroom again to be safe
        classroom = get_object_or_404(Classroom, id=classroom_id)
        classroom_students = classroom.students.all()
        
        for s in classroom_students:
            status = request.POST.get(f'status_{s.id}')
            if status:
                StudentAttendance.objects.update_or_create(
                    student=s,
                    date=date,
                    defaults={'status': status, 'marked_by': request.user}
                )
        
        messages.success(request, f"Attendance for {date} saved successfully.")
        return redirect(f"{request.path}?classroom={classroom_id}&date={date}")

    return render(request, 'admin_mark_attendance.html', {
        'classrooms': classrooms,
        'selected_classroom_id': int(selected_classroom_id) if selected_classroom_id else None,
        'selected_date': selected_date,
        'students': students,
        'user_notification_count': get_notifications(request.user)
    })

@login_required
def admin_profile(request):
    if request.user.role != 'school_admin':
        return redirect('login')

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = AdminProfileForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('school_admin_profile')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            profile_form = AdminProfileForm(instance=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('school_admin_profile')
    else:
        profile_form = AdminProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    user_notifications_count = get_notifications(request.user)
    
    return render(request, 'admin_profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_notification_count': user_notifications_count
    })
