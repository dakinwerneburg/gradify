from django.contrib import admin
from .models import Course, CourseWork, StudentSubmission, CourseStudent

admin.site.register(Course)
admin.site.register(CourseWork)
admin.site.register(StudentSubmission)
admin.site.register(CourseStudent)
