from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='school_admin_home'),
    path('dashboard/', views.admin_dashboard, name='school_admin_dashboard'),
    path('manage-users/', views.admin_manage_users, name='school_admin_manage_users'),
    path('edit-users/<str:id>', views.admin_edit_user, name='school_admin_edit_user'),
    path('add-users', views.admin_add_user, name='school_admin_add_user'),
    path('announcements', views.admin_announcements, name='school_admin_announcements'),
    path('add-announcements', views.admin_add_announcements, name='school_admin_add_announcements'),
    path('notifications', views.admin_user_notifications, name='school_admin_user_notifications'),
    path('announcement/<int:id>-<str:title>/', views.admin_single_announcement, name="school_admin_single_announcement"),
    path('edit-announcement/<int:id>/', views.admin_edit_announcement, name="school_admin_edit_announcement"),
    path('delete-announcement/<int:id>/', views.admin_delete_announcement, name="school_admin_delete_anouncement"),
    path('notification/<int:id>/', views.admin_single_notification, name="school_admin_single_notification"),
    path('analytics', views.admin_analytics, name="school_admin_analytics"),
    path('settings', views.admin_settings, name="school_admin_settings"),
    path('settings/grade-scale/add', views.admin_add_grade_scale, name="admin_add_grade_scale"),
    path('settings/grade-scale/delete/<int:id>', views.admin_delete_grade_scale, name="admin_delete_grade_scale"),
    
    # Session Management (Years & Terms)
    path('settings/academic-year/add', views.admin_add_academic_year, name="admin_add_academic_year"),
    path('settings/term/add', views.admin_add_term, name="admin_add_term"),
    path('settings/academic-year/toggle-active/<int:id>', views.admin_toggle_year_active, name="admin_toggle_year_active"),
    path('settings/term/toggle-active/<int:id>', views.admin_toggle_term_active, name="admin_toggle_term_active"),
    path('settings/term/toggle-publish/<int:id>', views.admin_toggle_term_publish, name="admin_toggle_term_publish"),
    path('settings/academic-year/delete/<int:id>', views.admin_delete_year, name="admin_delete_year"),
    path('settings/term/delete/<int:id>', views.admin_delete_term, name="admin_delete_term"),
    
    # Academic Management
    path('academic/', views.admin_academic_overview, name='admin_academic_overview'),
    path('academic/levels/', views.admin_manage_grade_levels, name='admin_manage_grade_levels'),
    path('academic/subjects/', views.admin_manage_subjects, name='admin_manage_subjects'),
    path('academic/classrooms/', views.admin_manage_classrooms, name='admin_manage_classrooms'),
    path('academic/class-subjects/', views.admin_manage_class_subjects, name='admin_manage_class_subjects'),
    path('academic/timetable/', views.admin_manage_timetable, name='admin_manage_timetable'),
    path('academic/timetable/<int:classroom_id>/', views.admin_manage_timetable, name='admin_manage_timetable'),
    path('academic/delete-timetable-slot/<int:slot_id>/', views.admin_delete_timetable_slot, name='admin_delete_timetable_slot'),
    # path('academic/calendar/', views.admin_school_calendar, name='admin_school_calendar'),

    # Edit/Delete Academic Assets
    path('academic/levels/edit/<int:id>/', views.admin_edit_grade_level, name='admin_edit_grade_level'),
    path('academic/levels/delete/<int:id>/', views.admin_delete_grade_level, name='admin_delete_grade_level'),
    path('academic/subjects/edit/<int:id>/', views.admin_edit_subject, name='admin_edit_subject'),
    path('academic/subjects/delete/<int:id>/', views.admin_delete_subject, name='admin_delete_subject'),
    path('academic/classrooms/edit/<int:id>/', views.admin_edit_classroom, name='admin_edit_classroom'),
    path('academic/classrooms/delete/<int:id>/', views.admin_delete_classroom, name='admin_delete_classroom'),
    path('academic/class-subjects/delete/<int:id>/', views.admin_delete_class_subject, name='admin_delete_class_subject'),
    
    # Student Promotion / Year End Rollover
    path('academic/promotion/', views.admin_student_promotion, name='admin_student_promotion'),
    path('academic/promotion/execute/', views.admin_promote_execute, name='admin_promote_execute'),
    # User Management Extensions
    path('delete-user/<str:id>/', views.admin_delete_user, name='school_admin_delete_user'),
    path('reset-password/<str:user_id>/', views.admin_reset_password, name='school_admin_reset_password'),
    path('calendar/', views.school_calendar, name='school_calendar'),
    path('calendar/delete/<int:id>/', views.admin_delete_calendar_event, name='admin_delete_calendar_event'),
    path('attendance/mark/', views.admin_mark_attendance, name='admin_mark_attendance'),
    path('edit-parent-profile/<str:custom_id>/', views.admin_edit_parent_profile, name='admin_edit_parent_profile'),
    path('profile/', views.admin_profile, name='school_admin_profile'),
]
