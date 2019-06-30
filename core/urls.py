"""
URLs file for core Gradify app.
"""
from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name="core/index.html")),
    path('course/', views.CoursesView.as_view(), name='course-list'),
    path('course/<int:pk>/gradebook/', views.StudentSubmissionsView.as_view(),
         name='studentsubmission-list'),
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('course/<int:pk>/roster/', views.CourseRosterView.as_view(), name='course-roster'),
    path('course/<int:pk>/<int:pk2>/', views.CourseWorkDetailView.as_view(), name='coursework-detail'),
]
