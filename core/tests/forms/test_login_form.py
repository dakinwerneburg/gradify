from django.test import TestCase
from allauth.account.forms import LoginForm


class LoginFormTest(TestCase):
    def test_blank_entries_fail(self):
        form_data = {'login': '', 'password': ''}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_username_placeholder_text(self):
        form = LoginForm()
        self.assertTrue(form.fields['login'].widget.attrs['placeholder'] == 'E-mail address')

    def test_password_placeholder_text(self):
        form = LoginForm()
        self.assertTrue(form.fields['password'].widget.attrs['placeholder'] == 'Password')
