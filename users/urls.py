from .views import SignUp
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path('signup/', SignUp.as_view(), name='signup'),
]
