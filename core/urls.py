"""
URLs file for core Gradify app.
"""
from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name="core/index.html")),
    path('courses/', views.CoursesView.as_view(), name='course-list'),
    path('courses/gradebook/', views.StudentSubmissionsView.as_view(),
         name='studentsubmission-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:pk>/roster/', views.view_course_roster, name='course-roster'),
]
