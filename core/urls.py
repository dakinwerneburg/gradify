"""
URLs file for core Gradify app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexPageView.as_view(), name='index'),
    path('courses/', views.CoursesView.as_view(), name='course-list'),
    path('courses/gradebook/', views.StudentSubmissionsView.as_view(),
         name='studentsubmission-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('accounts/password/change/', views.CustomPasswordChangeView.as_view(), name="account_password_change"),
    path('test_google_link/', views.TestGoogleLinkPageView.as_view(), name='test_google_link')
]
