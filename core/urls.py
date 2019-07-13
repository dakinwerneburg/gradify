"""
URLs file for core Gradify app.
"""
from django.urls import path, re_path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name="core/index.html"), name='home'),
    path('import/', views.gc_ingest_and_redirect, name='gc-import'),
    path('export/', views.export_csv_list_view, name='course-export'),
    # Course routes
    path('course/', views.CoursesView.as_view(), name='course-list'),
    path('course/create/', views.CourseCreateView.as_view(), name='course-create'),
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('course/<int:pk>/delete/', views.CourseDeleteView.as_view(), name="course-delete"),
    path('course/<int:pk>/gradebook/', views.StudentSubmissionsView.as_view(),
         name='studentsubmission-list'),
    path('course/<int:pk>/roster/', views.CourseRosterView.as_view(), name='course-roster'),
    path('course/<int:pk>/assignment/', views.CourseWorkListView.as_view(), name='coursework-list'),
    path('course/<int:pk>/assignment/<int:pk2>/', views.CourseWorkDetailView.as_view(),
         name='coursework-detail'),
    path('course/<int:pk>/assignment/<int:pk2>/update', views.CourseWorkUpdateView.as_view(),
         name='coursework-update'),
    # Assignment routes
    path('assignment/create/', views.CourseWorkCreateView.as_view(), name='coursework-create'),
    path('assignment/delete', views.CourseWorkDeleteView.as_view(), name='coursework-delete'),
    # Verification routes
    path('googleb95a6feb416ee79e.html', views.google_verification, name='google-verification'),
    re_path(r'^.well-known/acme-challenge/.*$', views.acme_challenge, name='acme-challenge'),
    # Gradebook change routes
    path('gradebook/studentsubmission/<int:pk>/update/',
         views.StudentSubmissionUpdateView.as_view(), name='studentsubmission-update'),
    path('gradebook/<int:pk>/studentsubmission/create/', views.StudentSubmissionCreateView.as_view(),
         name='studentsubmission-create'),

]
