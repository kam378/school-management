from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

# URLs accessible via the main domain (e.g., www.edumanage.com)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('super-admin/', include('myapps.super_admin.urls')),
    path('', include("myapps.core.urls")), # Landing page
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
