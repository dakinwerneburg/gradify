from django.urls import path
from . import views


urlpatterns = [
    path('google_classroom_list/', views.CourseTestView.as_view(), name='google_classroom_list')
]
