from django.urls import path
from . import views

app_name = 'learning_locker'

urlpatterns = [
    path('manage/', views.manage_resources, name='manage_resources'),
    path('hub/', views.student_locker, name='student_locker'),
    path('delete/<int:pk>/', views.delete_resource, name='delete_resource'),
]
