"""
URL configuration for school_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("myapps.core.urls")), # include the urls for the apps from their package and let their urls be preceded with their their names
    path('accounts/', include("myapps.accounts.urls")),
    path('school-admin/', include("myapps.school_admin.urls")),
    path('teacher/', include("myapps.teacher.urls")),
    path('student/', include("myapps.student.urls")),
    path('parent/', include("myapps.parent.urls")),
    path('whiteboard/', include("myapps.whiteboard.urls")),
    path('chat/', include("myapps.chat_system.urls")),
    path('attendance/', include("myapps.attendances.urls")),
    path('locker/', include("myapps.learning_locker.urls", namespace='learning_locker')),
]
