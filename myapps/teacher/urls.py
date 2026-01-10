from django.urls import path
from . import views

from myapps.school_admin.views import school_calendar

urlpatterns = [
    path('', views.teacher_dashboard, name='teacher_dashboard'),
    path('classes/', views.teacher_classes, name='teacher_classes'),
    path('gradebook/<int:class_subject_id>/', views.gradebook_view, name='teacher_gradebook'),
    path('assignments/', views.teacher_assignments, name='teacher_assignments'),
    path('assignments/add/', views.teacher_add_assignment, name='teacher_add_assignment'),
    path('assignments/edit/<int:assignment_id>/', views.teacher_edit_assignment, name='teacher_edit_assignment'),
    path('assignments/delete/<int:assignment_id>/', views.teacher_delete_assignment, name='teacher_delete_assignment'),
    path('grades/enter/', views.enter_grade, name='enter_grade'),
    path('timetable/', views.teacher_timetable, name='teacher_timetable'),
    path('calendar/', school_calendar, name='teacher_calendar'),
    path('profile/', views.teacher_profile, name='teacher_profile'),
]


