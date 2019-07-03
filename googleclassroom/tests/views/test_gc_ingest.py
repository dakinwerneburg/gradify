from django.test import TestCase


class ClassroomIngestViewTests(TestCase):
    fixtures = ['user']

    def test_error_msg_if_not_google_user(self):
        response = self.client.get('/googleclassroom/google_classroom_list', follow=True)
        error_msg = response.context['message']
        self.assertTrue('Please Sign In with a Google Account' in error_msg)
