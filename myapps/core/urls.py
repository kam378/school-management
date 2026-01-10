from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('impersonate/<str:token>/', views.impersonate_receive, name='impersonate_receive'),
    path('maintenance/', views.maintenance_view, name='maintenance'),
]