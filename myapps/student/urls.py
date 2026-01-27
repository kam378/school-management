from django.urls import path
from . import views
from myapps.school_admin.views import school_calendar

urlpatterns = [
    path('', views.student_dashboard, name="student_home"),
    path('dashboard/', views.student_dashboard, name="student_dashboard"),
    path('announcements/', views.student_announcements, name="student_announcements"),
    path('announcement/<int:id>-<str:title>/', views.student_single_announcement, name="student_single_annoucement"),
    path('timetable/', views.student_timetable, name="student_timetable"),
    path('assignments/', views.student_assignments, name="student_assignments"),
    path('assignment/<int:id>/', views.student_single_assignment, name="student_single_assignment"),
    path('attendance/', views.student_attendance, name="student_attendance"),
    path('grades/', views.student_grades, name="student_grades"),
    path('grades/detail/<int:class_subject_id>/', views.student_grade_detail, name="student_grade_detail"),
    path('report-card/', views.student_report_card, name="student_report_card"),
    path('profile/', views.student_profile, name="student_profile"),
    path('calendar/', school_calendar, name="student_calendar"),
]