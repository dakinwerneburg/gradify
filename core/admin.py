from django.contrib import admin
from .models import Course, Classroom, CourseWork, StudentSubmission, CourseStudent

admin.site.register(Course)
admin.site.register(Classroom)
admin.site.register(CourseWork)
admin.site.register(StudentSubmission)
admin.site.register(CourseStudent)

# @admin.register(ExampleModel)
# class ExampleModelAdmin(admin.ModelAdmin):
#    pass
