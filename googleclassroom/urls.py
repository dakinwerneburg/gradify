from django.urls import path
from . import views


urlpatterns = [
    path('', views.gc_ingest_and_redirect, name='gc_ingest'),
    path('google_classroom_list/', views.CourseTestView.as_view(), name='google_classroom_list')
]
