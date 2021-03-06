from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm
from allauth.account.views import PasswordChangeView


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'account/signup.html'


class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('login')
    template_name = 'account/password_change.html'
