from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import StudentProfileForm
from myapps.school_admin.models import Announcement, Classroom, ClassSubject, Timetable, SchoolSettings, GradeScale
from myapps.teacher.models import Assignment, Grade
from django.db.models import Avg

User = get_user_model()




# Create your views here.
def student_dashboard(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")

  # Multi-method classroom detection
  classroom = Classroom.objects.filter(students=request.user).first()
  if not classroom and hasattr(request.user, 'student_profile'):
      classroom = request.user.student_profile.classroom
  if not classroom:
      classroom = getattr(request.user, 'classrooms_enrolled', Classroom.objects.none()).first()
  
  upcoming_assignments = []
  average_grade = 0
  
  if classroom:
      # Today's Date
      from django.utils import timezone
      today = timezone.now().date()
      
      upcoming_assignments = Assignment.objects.filter(
          class_subject__classroom=classroom,
          due_date__gte=today
      ).order_by('due_date')[:5]
      
      # Calculate average grade
      grades = Grade.objects.filter(student=request.user)
      if grades.exists():
          avg_score = grades.aggregate(Avg('score'))['score__avg']
          average_grade = round(avg_score, 1)

  context = {
    "announcements" : Announcement.objects.all().order_by('-date')[:5],
    "classroom": classroom,
    "upcoming_assignments": upcoming_assignments,
    "average_grade": average_grade,
  }

  return render(request, "student_dashboard.html", context)


def student_announcements(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")

  announcements = Announcement.objects.all().order_by('-date')

  context = {
    "announcements" : announcements
  }

  return render(request, "student_announcements.html", context)

def student_single_announcement(request, id, title):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")

  announcement = Announcement.objects.get(id = id, title = title)

  context = {
    "announcement" : announcement
  }

  return render(request, "student_single_announcements.html", context)

def student_timetable(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  
  classroom = Classroom.objects.filter(students=request.user).first()
  timetable_data = {}
  days = Timetable.DAYS_OF_WEEK

  if classroom:
      slots = Timetable.objects.filter(class_subject__classroom=classroom)
      timetable_data = {day[0]: [] for day in days}
      for slot in slots:
          timetable_data[slot.day].append(slot)

  return render(request, "student_timetable.html", {
      'timetable_data': timetable_data,
      'days': days,
      'classroom': classroom
  })


def student_assignments(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  
  classroom = Classroom.objects.filter(students=request.user).first()
  assignments = []
  if classroom:
      assignments = Assignment.objects.filter(class_subject__classroom=classroom).order_by('due_date')

  return render(request, "student_assignments.html", {'assignments': assignments})


def student_single_assignment(request, id):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  
  assignment = get_object_or_404(Assignment, id=id)
  
  # Check if submission exists
  from myapps.teacher.models import StudentSubmission
  submission = StudentSubmission.objects.filter(assignment=assignment, student=request.user).first()
  
  if request.method == 'POST':
      if not assignment.is_interactive:
          messages.error(request, "This assignment accepts no submissions.")
          return redirect('student_single_assignment', id=id)

      submission_file = request.FILES.get('submission_file')
      submission_link = request.POST.get('submission_link')
      
      if submission_file or submission_link:
          if not submission:
              submission = StudentSubmission(assignment=assignment, student=request.user)
          
          if submission_file:
              submission.submission_file = submission_file
          if submission_link:
              submission.submission_link = submission_link
              
          submission.save()
          messages.success(request, "Assignment submitted successfully!")
          return redirect('student_single_assignment', id=id)
      else:
          messages.error(request, "Please provide a file or a link.")

  return render(request, "student_single_assignments.html", {'assignment': assignment, 'submission': submission})

def student_attendance(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  from myapps.school_admin.models import Term, SchoolSettings
  from myapps.attendances.models import StudentAttendance 
  from django.db.models import Q
  
  # Available terms: Published OR Active
  available_terms = Term.objects.filter(
      Q(is_published=True) | Q(is_active=True)
  ).order_by('-id') 
  
  selected_term_id = request.GET.get('term_id')
  selected_term = None
  
  if selected_term_id:
      selected_term = Term.objects.filter(id=selected_term_id).first()
  else:
      selected_term = Term.objects.filter(is_active=True).first() or available_terms.first()

  # Multi-method classroom detection
  classroom = Classroom.objects.filter(students=request.user).first()
  if not classroom and hasattr(request.user, 'student_profile'):
      classroom = request.user.student_profile.classroom
  if not classroom:
      classroom = getattr(request.user, 'classrooms_enrolled', Classroom.objects.none()).first()

  attendance_records = StudentAttendance.objects.filter(student=request.user).order_by('-date')
  
  if selected_term:
      attendance_records = attendance_records.filter(term=selected_term)
  
  # Statistics
  total = attendance_records.count()
  present = attendance_records.filter(status='present').count()
  late = attendance_records.filter(status='late').count()
  absent = attendance_records.filter(status='absent').count()
  rate = (present / total * 100) if total > 0 else 0

  settings = SchoolSettings.objects.first()

  context = {
      'classroom': classroom,
      'attendance_records': attendance_records,
      'total_days': total,
      'present_days': present,
      'late_days': late,
      'absent_days': absent,
      'attendance_rate': round(rate, 1),
      'available_terms': available_terms,
      'selected_term': selected_term,
      'school_settings': settings
  }
  return render(request, "student_attendance.html", context)

def student_grades(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  
  # Multi-method classroom detection
  classroom = Classroom.objects.filter(students=request.user).first()
  if not classroom and hasattr(request.user, 'student_profile'):
      classroom = request.user.student_profile.classroom
  if not classroom:
      classroom = getattr(request.user, 'classrooms_enrolled', Classroom.objects.none()).first()
  
  if not classroom:
      return render(request, "student_grades.html", {
          'grades_by_subject': {},
          'overall_gpa': 0,
          'total_subjects': 0
      })
  
  # Get all class subjects for this classroom
  class_subjects = ClassSubject.objects.filter(classroom=classroom).select_related('subject', 'teacher')
  
  # Group grades by subject
  grades_by_subject = {}
  total_percentage = 0
  subject_graded_count = 0
  
  for class_subject in class_subjects:
      # Get all grades for this subject
      subject_grades = Grade.objects.filter(
          student=request.user,
          assignment__class_subject=class_subject
      ).select_related('assignment').order_by('-graded_at')
      
      subject_percentage = 0
      letter_grade = 'N/A'
      
      if subject_grades.exists():
          # Calculate average for this subject
          total_score = sum(g.score for g in subject_grades)
          total_max = sum(g.assignment.max_score for g in subject_grades)
          subject_percentage = (total_score / total_max * 100) if total_max > 0 else 0
          
          # Determine letter grade
          if subject_percentage >= 90: letter_grade = 'A+'
          elif subject_percentage >= 85: letter_grade = 'A'
          elif subject_percentage >= 80: letter_grade = 'A-'
          elif subject_percentage >= 75: letter_grade = 'B+'
          elif subject_percentage >= 70: letter_grade = 'B'
          elif subject_percentage >= 65: letter_grade = 'B-'
          elif subject_percentage >= 60: letter_grade = 'C+'
          elif subject_percentage >= 55: letter_grade = 'C'
          else: letter_grade = 'F'
          
          total_percentage += subject_percentage
          subject_graded_count += 1
      
      grades_by_subject[class_subject.subject.name] = {
          'id': class_subject.id,
          'teacher': class_subject.teacher.get_full_name() if class_subject.teacher else "N/A",
          'letter_grade': letter_grade,
          'percentage': round(subject_percentage, 1) if subject_grades.exists() else 0,
          'grades': subject_grades,
          'has_grades': subject_grades.exists()
      }
  
  # Calculate overall GPA (4.0 scale)
  overall_percentage = (total_percentage / subject_graded_count) if subject_graded_count > 0 else 0
  if overall_percentage >= 90: overall_gpa = 4.0
  elif overall_percentage >= 85: overall_gpa = 3.7
  elif overall_percentage >= 80: overall_gpa = 3.3
  elif overall_percentage >= 75: overall_gpa = 3.0
  elif overall_percentage >= 70: overall_gpa = 2.7
  elif overall_percentage >= 65: overall_gpa = 2.3
  elif overall_percentage >= 60: overall_gpa = 2.0
  elif subject_graded_count > 0: overall_gpa = 1.0
  else: overall_gpa = 0.0
  
  context = {
      'grades_by_subject': grades_by_subject,
      'overall_gpa': overall_gpa,
      'total_subjects': class_subjects.count()
  }
  
  return render(request, "student_grades.html", context)


def student_report_card(request):
  """Generate a comprehensive report card with all academic data"""
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  
  from myapps.attendances.models import StudentAttendance
  from django.utils import timezone
  
  from django.db import connection
  
  # Multi-method classroom detection
  classroom = Classroom.objects.filter(students=request.user).first()
  if not classroom and hasattr(request.user, 'student_profile'):
      classroom = request.user.student_profile.classroom
  if not classroom:
      classroom = getattr(request.user, 'classrooms_enrolled', Classroom.objects.none()).first()

  # Get tenant name as fallback for school name
  tenant = getattr(connection, 'tenant', None)
  tenant_name = tenant.name if tenant else "School Management System"
  
  if not classroom:
      return render(request, "student_report_card.html", {
          'school_name': tenant_name,
          'grades_by_subject': {},
          'overall_gpa': 0,
          'classroom': None,
          'attendance_summary': {
              'total_days': 0, 'present_days': 0, 'late_days': 0, 'absent_days': 0, 'attendance_rate': 0
          },
          'total_subjects': 0,
          'overall_percentage': 0,
          'report_date': timezone.now()
      })
  
  # Get all class subjects for this classroom
  class_subjects = ClassSubject.objects.filter(classroom=classroom).select_related('subject', 'teacher')
  
  # Get school settings for weightage
  # --- Term Logic ---
  from myapps.school_admin.models import Term
  from django.db.models import Q
  
  available_terms = Term.objects.filter(Q(is_published=True) | Q(is_active=True)).order_by('-id')
  selected_term_id = request.GET.get('term_id')
  selected_term = None
  
  if selected_term_id:
      selected_term = Term.objects.filter(id=selected_term_id).first()
  else:
      selected_term = Term.objects.filter(is_active=True).first() or available_terms.first()

  if not selected_term:
      return render(request, "student_report_card.html", {
          'school_name': tenant_name,
          'grades_by_subject': {},
          'overall_gpa': 0,
          'classroom': classroom,
          'attendance_summary': {
              'total_days': 0, 'present_days': 0, 'late_days': 0, 'absent_days': 0, 'attendance_rate': 0
          },
          'total_subjects': 0,
          'overall_percentage': 0,
          'report_date': timezone.now(),
          'no_terms': True # Flag for template
      })

  settings = SchoolSettings.objects.first()
  cass_w = settings.cass_weight if settings else 40
  exam_w = settings.exam_weight if settings else 60
  
  # Get all grade scales ordered by highest percentage first
  grade_scales = list(GradeScale.objects.all().order_by('-min_percentage'))
  
  # Group grades by subject with detailed breakdown
  grades_by_subject = {}
  total_final_percentage = 0
  subject_graded_count = 0
  
  for class_subject in class_subjects:
      # Get all grades for this subject
      all_grades = Grade.objects.filter(
          student=request.user,
          assignment__class_subject=class_subject
      ).select_related('assignment')

      if selected_term:
          all_grades = all_grades.filter(assignment__term=selected_term)
      
      # Filter by Term if selected
      if selected_term:
          all_grades = all_grades.filter(assignment__term=selected_term)
      
      cass_grades = [g for g in all_grades if g.assignment.category == 'cass']
      exam_grades = [g for g in all_grades if g.assignment.category == 'exam']
      
      # Calculate CASS Percentage
      cass_score = sum(g.score for g in cass_grades)
      cass_max = sum(g.assignment.max_score for g in cass_grades)
      cass_pct = float(cass_score / cass_max * 100) if cass_max > 0 else 0.0
      
      # Calculate Exam Percentage
      exam_score = sum(g.score for g in exam_grades)
      exam_max = sum(g.assignment.max_score for g in exam_grades)
      exam_pct = float(exam_score / exam_max * 100) if exam_max > 0 else 0.0
      
      # Combined Weighted Percentage
      # Formula: (CASS_AVG * CASS_W / 100) + (EXAM_AVG * EXAM_W / 100)
      final_subject_pct = (cass_pct * cass_w / 100) + (exam_pct * exam_w / 100)
      
      letter_grade = 'F'
      grade_point = 0.0
      badge_color = '#dc3545'
      
      # Match against GradeScale
      for scale in grade_scales:
          if final_subject_pct >= float(scale.min_percentage):
              letter_grade = scale.label
              grade_point = float(scale.grade_point)
              badge_color = scale.color_code
              break
      
      if all_grades.exists():
          grades_by_subject[class_subject.id] = {
              'subject': class_subject.subject.name,
              'teacher': class_subject.teacher.get_full_name() if class_subject.teacher else "TBA",
              'cass_pct': round(cass_pct, 1),
              'exam_pct': round(exam_pct, 1),
              'final_pct': round(final_subject_pct, 1),
              'letter_grade': letter_grade,
              'grade_point': grade_point,
              'badge_color': badge_color,
          }
          total_final_percentage += final_subject_pct
          subject_graded_count += 1
  
  # Calculate overall GPA based on subject grade points
  overall_gp_sum = sum(data['grade_point'] for data in grades_by_subject.values())
  overall_gpa = (overall_gp_sum / subject_graded_count) if subject_graded_count > 0 else 0
  overall_percentage = (total_final_percentage / subject_graded_count) if subject_graded_count > 0 else 0
  
  # Get attendance summary
  attendance_qs = StudentAttendance.objects.filter(student=request.user)
  if selected_term:
      attendance_qs = attendance_qs.filter(term=selected_term)
      
  total_days = attendance_qs.count()
  present_days = attendance_qs.filter(status='present').count()
  late_days = attendance_qs.filter(status='late').count()
  absent_days = attendance_qs.filter(status='absent').count()
  attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
  
  attendance_summary = {
      'total_days': total_days,
      'present_days': present_days,
      'late_days': late_days,
      'absent_days': absent_days,
      'attendance_rate': round(attendance_rate, 1)
  }
  
  context = {
      'school_name': tenant_name,
      'grades_by_subject': grades_by_subject,
      'overall_gpa': round(overall_gpa, 2),
      'overall_percentage': round(overall_percentage, 1),
      'total_subjects': class_subjects.count(),
      'classroom': classroom,
      'attendance_summary': attendance_summary,
      'report_date': timezone.now(),
      'cass_weight': cass_w,
      'exam_weight': exam_w,
      'available_terms': available_terms,
      'selected_term': selected_term,
  }
  
  return render(request, "student_report_card.html", context)


def student_profile(request):
    if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
        return redirect("login")
    
    profile_form = StudentProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = StudentProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect('student_profile')
            else:
                messages.error(request, "Please correct the errors below.")
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, "Your password has been changed successfully!")
                return redirect('student_profile')
            else:
                messages.error(request, "Password change failed. Please check the requirements.")

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, "student_profile.html", context)


def student_grade_detail(request, class_subject_id):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
    
  class_subject = get_object_or_404(ClassSubject, id=class_subject_id)
  from myapps.school_admin.models import Term, SchoolSettings, GradeScale
  from django.db.models import Q
  
  settings = SchoolSettings.objects.first()
  current_term = Term.objects.filter(is_active=True).first()
  
  # Fetch all grades for this subject and student
  grades = Grade.objects.filter(
      student=request.user, 
      assignment__class_subject=class_subject
  ).select_related('assignment').order_by('-graded_at')
  
  # Term filtering if available
  term_id = request.GET.get('term_id')
  if term_id:
      grades = grades.filter(assignment__term_id=term_id)
  elif current_term:
      grades = grades.filter(assignment__term=current_term)

  # Breakdown
  cass_grades = [g for g in grades if g.assignment.category == 'cass']
  exam_grades = [g for g in grades if g.assignment.category == 'exam']
  
  # Stats
  cass_w = settings.cass_weight if settings else 40
  exam_w = settings.exam_weight if settings else 60
  
  cass_score = sum(g.score for g in cass_grades)
  cass_max = sum(g.assignment.max_score for g in cass_grades)
  cass_pct = (cass_score / cass_max * 100) if cass_max > 0 else 0
  
  exam_score = sum(g.score for g in exam_grades)
  exam_max = sum(g.assignment.max_score for g in exam_grades)
  exam_pct = (exam_score / exam_max * 100) if exam_max > 0 else 0
  
  final_pct = (cass_pct * cass_w / 100) + (exam_pct * exam_w / 100)
  
  # Match Grade
  letter_grade = 'F'
  badge_color = '#dc3545'
  for scale in GradeScale.objects.all().order_by('-min_percentage'):
      if final_pct >= float(scale.min_percentage):
          letter_grade = scale.label
          badge_color = scale.color_code
          break

  return render(request, "student_grade_detail.html", {
      'class_subject': class_subject,
      'grades': grades,
      'cass_pct': round(cass_pct, 1),
      'exam_pct': round(exam_pct, 1),
      'final_pct': round(final_pct, 1),
      'letter_grade': letter_grade,
      'badge_color': badge_color,
      'available_terms': Term.objects.filter(Q(is_active=True) | Q(is_published=True)),
      'school_settings': settings
  })

