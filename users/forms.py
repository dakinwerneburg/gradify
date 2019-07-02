from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import LoginForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ['username', 'email', 'organization', 'first_name', 'last_name']


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class MyCustomLoginForm(LoginForm):


    def login(self, *args, **kwargs):
        # You must return the original result.
        return super(MyCustomLoginForm, self).login(*args, **kwargs)