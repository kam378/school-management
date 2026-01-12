from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

# URLs accessible ONLY via subdomains (e.g., school1.edumanage.com)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("myapps.core.urls")), # Login page essentially
    path('accounts/', include("myapps.accounts.urls")),
    path('school-admin/', include("myapps.school_admin.urls")),
    path('teacher/', include("myapps.teacher.urls")),
    path('student/', include("myapps.student.urls")),
    path('parent/', include("myapps.parent.urls")),
    path('whiteboard/', include("myapps.whiteboard.urls")),
    path('chat/', include("myapps.chat_system.urls")),
    path('attendance/', include("myapps.attendances.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
