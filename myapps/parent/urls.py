from django.urls import path
from . import views
from myapps.school_admin.views import school_calendar

urlpatterns = [
    path('', views.parent_dashboard, name='parent_home'),
    path('dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('announcements/', views.parent_announcements, name='parent_announcements'),
    path('results/<str:student_id>/', views.parent_child_results, name='parent_child_results'),
    path('calendar/', school_calendar, name='parent_calendar'),
    path('profile/', views.parent_profile, name='parent_profile'),
]