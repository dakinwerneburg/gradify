from .views import SignUp
from django.urls import path

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
]
