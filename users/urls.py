from .views import SignUp
from django.urls import include, path

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
]
