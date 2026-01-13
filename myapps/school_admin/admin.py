from django.contrib import admin
from .models import Announcement, SchoolSettings, GradeScale

# Register your models here.
admin.site.register(Announcement)
admin.site.register(SchoolSettings)
admin.site.register(GradeScale)