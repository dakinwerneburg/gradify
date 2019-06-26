"""
URLs file for core Gradify app.
"""
from django.urls import path
from django.views.generic import TemplateView
from . import views
from .views import IndexPageView

urlpatterns = [
    path('', views.IndexPageView.as_view(), name='index'),
    path('courses/', views.CoursesView.as_view(), name='course-list'),
    path('courses/gradebook/', views.StudentSubmissionsView.as_view(),
         name='studentsubmission-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('test_google_link/', views.TestGoogleLinkPageView.as_view(), name='test_google_link')
]
