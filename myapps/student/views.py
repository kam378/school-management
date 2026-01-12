from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import StudentProfileForm
from myapps.school_admin.models import Announcement, Classroom, ClassSubject, Timetable
from myapps.teacher.models import Assignment, Grade
from django.db.models import Avg

User = get_user_model()




# Create your views here.
def student_dashboard(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")

  # Get student's classroom
  classroom = Classroom.objects.filter(students=request.user).first()
  
  upcoming_assignments = []
  average_grade = 0
  
  if classroom:
      # Get assignments for the classes the student is in
      upcoming_assignments = Assignment.objects.filter(class_subject__classroom=classroom).order_by('due_date')[:3]
      
      # Calculate average grade
      grades = Grade.objects.filter(student=request.user)
      if grades.exists():
          avg_score = grades.aggregate(Avg('score'))['score__avg']
          # Assuming grades are percentages or normalizing to 100
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
  return render(request, "student_attendance.html")

def student_grades(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  
  grades = Grade.objects.filter(student=request.user).order_by('-graded_at')
  
  # Group grades by subject for better visualization if needed
  # Simplified for now
  return render(request, "student_grades.html", {'grades': grades})


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


def student_grade_detail(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  return render(request, "student_grade_detail.html")

def student_report_card(request):
  if not request.user.is_authenticated or not request.user.is_active or not request.user.role == "student":
    return redirect("login")
  return render(request, "student_report_card.html")