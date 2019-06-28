"""
URLs file for core Gradify app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CoursesView.as_view(), name='course'),
    path('index/', views.IndexPageView.as_view(), name='index'),
    path('course/', views.CoursesView.as_view(), name='course-list'),
    path('course/<int:pk>/gradebook/', views.StudentSubmissionsView.as_view(),
         name='studentsubmission-list'),
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail')
]
