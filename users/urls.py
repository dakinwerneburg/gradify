from .views import SignUp
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('accounts/password/change/', views.CustomPasswordChangeView.as_view(), name="account_password_change")
]
