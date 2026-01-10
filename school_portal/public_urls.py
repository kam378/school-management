from django.contrib import admin
from django.urls import path, include

# URLs accessible via the main domain (e.g., www.edumanage.com)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('super-admin/', include('myapps.super_admin.urls')),
    path('', include("myapps.core.urls")), # Landing page
]
