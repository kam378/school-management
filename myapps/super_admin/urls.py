from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='super_admin_dashboard'),
    path('schools/', views.tenant_list, name='super_admin_schools'),
    path('schools/create/', views.tenant_create, name='super_admin_create'),
    path('schools/edit/<int:pk>/', views.tenant_edit, name='super_admin_edit'),
    path('schools/delete/<int:pk>/', views.tenant_delete, name='super_admin_delete'),
    path('schools/impersonate/<int:pk>/', views.impersonate_tenant, name='super_admin_impersonate'),
    path('maintenance/toggle/', views.toggle_maintenance, name='toggle_maintenance'),
    path('plans/', views.plan_list, name='super_admin_plans'),
    path('plans/create/', views.plan_create, name='super_admin_plan_create'),
    path('plans/edit/<int:pk>/', views.plan_edit, name='super_admin_plan_edit'),
    path('plans/delete/<int:pk>/', views.plan_delete, name='super_admin_plan_delete'),
    path('settings/', views.system_settings, name='system_settings'),
    path('users/', views.super_admin_user_list, name='super_admin_users'),
    path('users/create/', views.super_admin_user_create, name='super_admin_user_create'),
    path('users/edit/<int:pk>/', views.super_admin_user_edit, name='super_admin_user_edit'),
    path('users/delete/<int:pk>/', views.super_admin_user_delete, name='super_admin_user_delete'),
    path('resources/', views.manage_platform_resources, name='manage_platform_resources'),
    path('resources/delete/<int:pk>/', views.delete_platform_resource, name='delete_platform_resource'),
    path('audit-logs/', views.platform_audit_logs, name='platform_audit_logs'),
]


